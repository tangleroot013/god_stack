# ==============================================================================
# MATRIX ORCHESTRATOR WITH DEDUPLICATION & STRUCTURAL PARSING
# Architecture: Relational Processing Core with Concurrent Latency Verification
# ==============================================================================
import asyncio
import time
import logging
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from matrix_storage import MatrixStorage
from scavenger import ProxyScavenger
from god_scraper import GodScraper
from url_sanitizer import UrlSanitizer

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[ORCHESTRATOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixOrchestrator")

class CoreMatrixOrchestrator:
    def __init__(self):
        self.storage = MatrixStorage()
        self.scavenger = ProxyScavenger()
        self.scraper = None
        self.proxy_scoreboard = []
        self.proxy_index = 0

    async def initialize_system(self):
        await self.storage.initialize_vault()
        logger.info("Initializing active fallback proxy lists...")
        raw_proxies = await self.scavenger.run()
        
        if raw_proxies:
            await self.build_proxy_scoreboard(raw_proxies)
        else:
            logger.warning("No public proxy routes verified. Operating on direct home network interfaces.")
            self.proxy_scoreboard = [{"proxy": None, "latency": 0.0}]

    async def _test_single_proxy_latency(self, proxy_url: str) -> dict:
        test_target = "https://news.ycombinator.com"
        start_time = time.time()
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=3.0) as client:
                response = await client.get(test_target)
                if response.status_code == 200:
                    return {"proxy": proxy_url, "latency": (time.time() - start_time) * 1000}
        except Exception:
            pass
        return {"proxy": proxy_url, "latency": 9999.0}

    async def build_proxy_scoreboard(self, raw_proxies: list):
        tasks = [self._test_single_proxy_latency(p) for p in raw_proxies]
        results = await asyncio.gather(*tasks)
        self.proxy_scoreboard = sorted([r for r in results if r["latency"] < 9999.0], key=lambda x: x["latency"])
        if not self.proxy_scoreboard:
            self.proxy_scoreboard = [{"proxy": None, "latency": 0.0}]

    def _get_optimal_proxy(self) -> str:
        if not self.proxy_scoreboard:
            return None
        proxy_data = self.proxy_scoreboard[self.proxy_index % len(self.proxy_scoreboard)]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxy_scoreboard)
        return proxy_data["proxy"]

    def _parse_structural_data(self, html_content: str) -> dict:
        """Custom structural parser targeting titles, metadata, and author targets."""
        extracted = {"title": "Unknown", "author": "Anonymous", "time": "N/A"}
        if not html_content:
            return extracted
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Target page title
            title_node = soup.find('title')
            if title_node:
                extracted["title"] = title_node.get_text(strip=True)
                
            # HackerNews specific structural parsing rule examples
            hn_user = soup.find('a', class_='hnuser')
            if hn_user:
                extracted["author"] = hn_user.get_text(strip=True)
                
            age_span = soup.find('span', class_='age')
            if age_span and age_span.has_attr('title'):
                extracted["time"] = age_span['title'] # ISO timestamp if available
        except Exception as e:
            logger.error(f"Structural data mining extraction fault: {str(e)}")
        return extracted

    def _extract_page_links(self, base_url: str, html_content: str) -> list:
        discovered = []
        if not html_content:
            return discovered
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for anchor in soup.find_all('a', href=True):
                absolute_url = urljoin(base_url, anchor['href'])
                clean_url = UrlSanitizer.normalize(absolute_url)
                if clean_url and "news.ycombinator.com" in clean_url:
                    if clean_url not in discovered:
                        discovered.append(clean_url)
        except Exception:
            pass
        return discovered

    async def process_next_job(self) -> bool:
        try:
            job = await self.storage.fetch_next_job()
        except Exception as e:
            logger.error(f"Database extraction pipeline failure: {str(e)}")
            return False

        if not job or not isinstance(job, (list, tuple)) or len(job) < 2:
            return False

        job_id, target_url = job[0], job[1]
        logger.info(f"Processing Job ID [ {job_id} ] -> Targeting: {target_url}")

        selected_proxy = self._get_optimal_proxy()
        success = False
        payload_result = None

        for attempt in range(3):
            try:
                self.scraper = GodScraper()
                await self.scraper.initialize(headless=True, proxy_url=selected_proxy)
                
                workflow_steps = [{"action": "wait_for", "target": "body"}]
                payload_result = await self.scraper.scrape(target_url, workflow=workflow_steps)
                
                if payload_result and payload_result.get("status") == "success":
                    success = True
                    break
            except Exception as loop_fault:
                logger.error(f"⚠️ Proxy route failed: {str(loop_fault)}")
                selected_proxy = self._get_optimal_proxy()
            finally:
                if self.scraper:
                    await self.scraper.shutdown()

        final_state = "COMPLETED" if success else "FAILED"
        await self.storage.update_job_status(job_id, final_state)

        if success and payload_result:
            raw_html = payload_result.get("html", "")
            
            # Feature 2: Structured Parsing
            meta = self._parse_structural_data(raw_html)
            logger.info(f"📑 Parsed Metadata -> Title: '{meta['title']}' | Author: {meta['author']}")

            # Feature 1: Deduplicated discovery outlink filtering
            child_links = self._extract_page_links(target_url, raw_html)
            valid_seeds = []
            
            for link in child_links:
                # Deduplication check: verify if the URL exists anywhere in our database
                if not await self.storage.check_url_exists(link):
                    valid_seeds.append(link)

            if valid_seeds:
                logger.info(f"🔗 Discovery Loop: {len(valid_seeds)} unique child endpoints verified. Seeding matrix...")
                await self.storage.seed_job_matrix(valid_seeds[:5])

            # Commit the record including structural text
            await self.storage.commit_payload(
                url=target_url,
                title=meta["title"],
                markdown=payload_result.get("markdown", ""),
                proxy=str(selected_proxy)
            )
            
        logger.info(f"Job ID [ {job_id} ] fully updated to state: [ {final_state} ]\n")
        return True
