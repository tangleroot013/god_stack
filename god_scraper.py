import asyncio
import logging
from typing import List, Optional
from frontier_manager import Frontier
from god_engine import GodEngineNode
from metrics_exporter import SYSTEM_METRICS

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[GOD-SCRAPER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, concurrency_limit: int = 10, profile_name: str = "default"):
        self.concurrency_limit = concurrency_limit
        self.profile_name = profile_name
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.active = False

    async def initialize(self, headless: bool = True, proxy_url: Optional[str] = None):
        """Prepares worker matrices and underlying extraction dependencies with proxy routing."""
        logger.info(f"Initializing unified scraping engine runner sequence [Profile: {self.profile_name}]...")
        if proxy_url:
            logger.info(f"Stealth configuration attached to proxy egress vector: {proxy_url}")
        
        await GodEngineNode.initialize(headless=headless)
        self.active = True
        logger.info(f"Scraper sequence active. Concurrency ceiling set to: {self.concurrency_limit}")

    async def process_target(self, url: str) -> None:
        """
        Handles a single extraction round for a target URL.
        Respects global concurrency limits, forwards context profiles, and extracts failures.
        """
        async with self.semaphore:
            if not self.active:
                return

            try:
                SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
                
                # Corrected: Explicitly forward the targeted stealth configuration profile profile_name
                result = await GodEngineNode.fetch_and_extract(url, profile=self.profile_name)

                if result.get("status") == "SUCCESS":
                    links = result.get("extracted_data", {}).get("links", [])
                    if links:
                        logger.info(f"[{self.profile_name}] Discovered {len(links)} outbound routes from {url}")
                    SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
                else:
                    # Enriched Failure Tracking: Log precise trace issues from internal exceptions
                    msg = result.get("message") or result.get("error") or "Unknown internal execution termination"
                    logger.warning(f"[{self.profile_name}] Extraction failed for {url}: {msg}")
            except Exception as exc:
                logger.error(f"[{self.profile_name}] Mission exception trace for {url}: {str(exc)}")

    def _get_next_targets(self, batch_size: int = 5) -> List[str]:
        """Safely pools targets from active upstream pipelines."""
        targets = []
        for queue_name in ["high_priority", "standard", "discovery"]:
            q = Frontier.get_queue(queue_name)
            if q:
                for _ in range(batch_size - len(targets)):
                    try:
                        res = q.get_nowait()
                        if res: 
                            targets.append(res)
                    except:
                        break
                if targets:
                    return targets
        return targets

    async def start_orchestration_loop(self, runtime_limit_ticks: Optional[int] = None):
        """Continually drains active Frontier queues until system teardown is triggered."""
        logger.info("Entering operational extraction matrix runloop...")
        ticks = 0

        while self.active:
            if runtime_limit_ticks and ticks >= runtime_limit_ticks:
                logger.info("Graceful execution tick threshold surpassed. Stopping runloop.")
                break

            next_targets = self._get_next_targets(batch_size=5)
            
            if not next_targets:
                await asyncio.sleep(0.1)
                ticks += 1
                continue

            tasks = [asyncio.create_task(self.process_target(url)) for url in next_targets]
            await asyncio.gather(*tasks)
            ticks += 1

    async def shutdown(self):
        """Terminates engine tasks and cleans workspace pipeline states."""
        logger.info("Executing graceful scraper teardown sequence...")
        self.active = False
        await GodEngineNode.shutdown()
        logger.info("Scraper core subsystem deactivated successfully.")

# Global production singleton scraper deployment node
GodScraperNode = GodScraper()
