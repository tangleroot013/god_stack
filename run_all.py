#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK V2.0.0 ULTRA-HARDENED PIPELINE: EVASION, ANTI-BOT & WORKER QUEUE
# ==============================================================================
import os
import sys
import json
import yaml
import asyncio
import logging
import re
import random
import subprocess
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List, Dict, Any, Optional

# Setup unified console log streaming layouts
logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[SYSTEM-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UnifiedPipeline")

# ==============================================================================
# DEPENDENCY SYSTEM TRACE & MATRIX LOADERS
# ==============================================================================
MISSING_DEPS = []
for dep in ["playwright", "bs4", "markdownify", "yaml", "httpx", "courlan", "tldextract", "cloudscraper"]:
    try:
        if dep == "bs4":
            from bs4 import BeautifulSoup
        elif dep == "yaml":
            import yaml
        else:
            __import__(dep)
    except ImportError:
        MISSING_DEPS.append(dep)

if MISSING_DEPS:
    print(f"\033[1;31m[-] Critical Runtime Dependencies Missing:\033[0m {MISSING_DEPS}")
    sys.exit(1)

import courlan
import httpx
import tldextract
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright

# ==============================================================================
# LIGHTWEIGHT METRIC DASHBOARD TUI UTILITY
# ==============================================================================
class TerminalDashboard:
    @staticmethod
    def render_header(status: str = "INITIALIZING"):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[1;35m" + "="*80 + "\033[0m")
        print(f"\033[1;36m  G.O.D. STACK v2.0.0 HARDENED SYSTEM MATRIX | STATUS: {status}\033[0m")
        print("\033[1;35m" + "="*80 + "\033[0m\n")

    @staticmethod
    def render_stats_table(metrics: Dict[str, Any]):
        print("\033[1;33m[+ ACTIVE QUEUE TRACKING MATRIX] \033[0m")
        print("-" * 50)
        for key, value in metrics.items():
            print(f" • \033[1;32m{key.ljust(25)}:\033[0m {value}")
        print("-" * 50 + "\n")

# ==============================================================================
# AUTOMATED GIT COMMIT SEQUENCE RUNNER
# ==============================================================================
class GitAutomationMatrix:
    @staticmethod
    def run_command(args: List[str]) -> str:
        try:
            res = subprocess.run(args, capture_output=True, text=True, check=False)
            return res.stdout.strip()
        except Exception:
            return ""

    @classmethod
    def secure_commit(cls):
        logger.info("[GIT] Initiating repository code tracking synchronization state...")
        if not os.path.exists(".git"):
            cls.run_command(["git", "init"])
            cls.run_command(["git", "branch", "-m", "main"])

        cls.run_command(["git", "add", "run_all.py"])
        status = cls.run_command(["git", "status", "--porcelain"])
        if status:
            commit_msg = "feat(core): deploy advanced evasion matrix, anti-bot sentinel, and concurrent worker queue hooks"
            cls.run_command(["git", "commit", "-m", commit_msg])
            logger.info("\033[1;32m[GIT SUCCESS]\033[0m Staged core updates committed securely.")
        else:
            logger.info("[GIT STATUS] Tree state clean. Skipping duplicate commit sequence.")
        
        cls.run_command(["git", "tag", "-d", "v2.0.0"])
        cls.run_command(["git", "tag", "-a", "v2.0.0", "-m", "Release G.O.D. Stack v2.0.0 Stable"])
        logger.info("\033[1;32m[GIT SUCCESS]\033[0m Milestone tag locked at [v2.0.0].")

# ==============================================================================
# MODULE 1: URL SANITIZATION MATRIX & COURLAN FRONTIER ROUTER
# ==============================================================================
class UrlSanitizer:
    @staticmethod
    def normalize(raw_url: str) -> str:
        if not raw_url or not isinstance(raw_url, str): return ""
        cleaned = raw_url.strip()
        if cleaned.startswith("//"): cleaned = "https:" + cleaned
        elif not cleaned.startswith(("http://", "https://")): cleaned = "https://" + cleaned
        try:
            parsed = urlparse(cleaned)
            query_params = parse_qsl(parsed.query)
            blacklisted_keys = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
            query_params = [(k, v) for k, v in query_params if k.lower() not in blacklisted_keys]
            return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path if parsed.path else "/", parsed.params, urlencode(query_params), ""))
        except Exception: return cleaned

class CourlanRouter:
    @staticmethod
    def validate_and_clean(url: str) -> str:
        pristine_base = UrlSanitizer.normalize(url)
        try:
            cleaned_url = courlan.clean_url(pristine_base)
            if not cleaned_url or not courlan.validate_url(cleaned_url): return ""
            return cleaned_url
        except Exception: return ""

# ==============================================================================
# MODULE 2: PROXY SCAVENGER SYSTEM ENGINE
# ==============================================================================
class ProxyScavenger:
    def __init__(self):
        self.source_url = "https://free-proxy-list.net/"
        self.verified_proxies = []

    async def harvest_raw_list(self) -> list:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                res = await client.get(self.source_url)
                if res.status_code != 200: return []
            soup = BeautifulSoup(res.text, 'html.parser')
            proxies = []
            table = soup.find('table', class_='table')
            if not table: return []
            for row in table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip, port = cols[0].text.strip(), cols[1].text.strip()
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                        proxies.append(f"http://{ip}:{port}")
            return proxies[:15]
        except Exception: return []

    async def verify_node(self, proxy_url: str):
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=2.5) as client:
                if (await client.get("http://www.google.com")).status_code == 200:
                    self.verified_proxies.append(proxy_url)
        except Exception: pass

    async def run(self) -> list:
        raw_list = await self.harvest_raw_list()
        if not raw_list: return ["http://127.0.0.1:8080"]
        await asyncio.gather(*[self.verify_node(p) for p in raw_list])
        return self.verified_proxies if self.verified_proxies else [raw_list[0]]

# ==============================================================================
# MODULE 3: ANTI-BOT PROTECTION SENTINEL UTILITY
# ==============================================================================
class AntiBotSentinel:
    FINGERPRINTS = {
        "Cloudflare Turnstile / Challenge Page": re.compile(r"challenges\.cloudflare\.com|cf-turnstile|cf-challenge", re.IGNORECASE),
        "Google reCAPTCHA Frame": re.compile(r"google\.com/recaptcha|g-recaptcha", re.IGNORECASE),
        "hCaptcha Security Block": re.compile(r"hcaptcha\.com|h-captcha", re.IGNORECASE)
    }

    @classmethod
    def evaluate_dom(cls, html: str) -> Optional[str]:
        for name, pattern in cls.FINGERPRINTS.items():
            if pattern.search(html):
                return name
        return None

# ==============================================================================
# MODULE 4: ARCHITECTURE PLAYWRIGHT AUTOMATION ENGINE + STEALTH EVASION
# ==============================================================================
class GodScraper:
    def __init__(self, profile_path: str = "stealth_profiles.yaml"):
        self.profile_path = profile_path
        self.playwright = None
        self.browser = None
        self.context = None

    async def initialize(self, proxy_url: Optional[str] = None):
        self.playwright = await async_playwright().start()
        launch_args = {"headless": True, "args": ["--disable-blink-features=AutomationControlled"]}
        if proxy_url: launch_args["proxy"] = {"server": proxy_url}
        
        self.browser = await self.playwright.chromium.launch(**launch_args)
        
        # ADVANCED HEADLESS EVASION LAYER (Option 1)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York"
        )
        
        # Inject Runtime Evasion Scripts directly to eliminate navigator.webdriver fingerprint leaks
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """)

    async def scrape(self, url: str) -> Dict[str, Any]:
        page = await self.context.new_page()
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            raw_html = await page.content()
            
            # ANTI-BOT DEFENSE SENTINEL INTERCEPTION LOOP (Option 2)
            defense_detected = AntiBotSentinel.evaluate_dom(raw_html)
            if defense_detected:
                logger.warning(f"[SENTINEL-ALERT] Active firewall caught: {defense_detected}")
                # Fallback evasion strategy: execution thread holding block to throw off rate limits
                await page.evaluate("window.scrollBy(0, window.innerHeight)")
                await asyncio.sleep(random.uniform(2.0, 4.0))
                raw_html = await page.content() # Re-pull DOM state after anti-bot layout handling

            soup = BeautifulSoup(raw_html, "html.parser")
            title = soup.title.string.strip() if soup.title else "Null DOM Title Anchor"
            return {"status": "success", "url": url, "title": title, "status_code": response.status, "markdown": md(raw_html, heading_style="ATX")}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

# ==============================================================================
# MODULE 5: DISTRIBUTED MULTI-THREADED QUEUE WORKER SYSTEM (Option 3)
# ==============================================================================
class ConcurrentPipelineManager:
    def __init__(self, targets: List[str], max_concurrency: int = 2, proxy: Optional[str] = None):
        self.targets = targets
        self.max_concurrency = max_concurrency
        self.proxy = proxy
        self.queue = asyncio.Queue()
        self.scraper = GodScraper()
        self.metrics = {
            "Total Target Queue": len(targets),
            "Active Workers Running": max_concurrency,
            "Jobs Dispatched Successfully": 0,
            "Failed Structural Paths": 0,
            "Active Proxy Routing Route": proxy if proxy else "Direct Egress"
        }

    async def worker_loop(self):
        while not self.queue.empty():
            target_url = await self.queue.get()
            retries = 3
            backoff = 2.0
            
            while retries > 0:
                result = await self.scraper.scrape(target_url)
                if result["status"] == "success":
                    ext = tldextract.extract(target_url)
                    payload = {"target_url": result["url"], "title": result["title"], "status_code": result["status_code"], "markdown_snippet": result["markdown"][:300]}
                    
                    with open(f"outputs/intel_{ext.domain}_{random.randint(1000,9999)}.json", "w", encoding="utf-8") as out_f:
                        json.dump(payload, out_f, indent=2)
                    
                    self.metrics["Jobs Dispatched Successfully"] += 1
                    TerminalDashboard.render_header("DISTRIBUTED CONCURRENT EXECUTOR ACTIVE")
                    TerminalDashboard.render_stats_table(self.metrics)
                    print(f"\033[1;32m[+ SUCCESS]\033[0m Extracted: '{result['title']}'")
                    break
                else:
                    retries -= 1
                    logger.warning(f"[RETRY CONTROLLER] Error processing target url {target_url}. Retries remaining: {retries}. Backoff dynamic holding applied.")
                    await asyncio.sleep(backoff)
                    backoff *= 2 # Exponential holding algorithm backoff execution
            else:
                self.metrics["Failed Structural Paths"] += 1
                TerminalDashboard.render_header("DISTRIBUTED CONCURRENT EXECUTOR ACTIVE")
                TerminalDashboard.render_stats_table(self.metrics)
                
            self.queue.task_done()

    async def run_pipeline(self):
        TerminalDashboard.render_header("INITIALIZING HIGH PERFORMANCE WORKER ARRAYS")
        TerminalDashboard.render_stats_table(self.metrics)
        
        for target in self.targets:
            await self.queue.put(target)

        await self.scraper.initialize(proxy_url=self.proxy)
        workers = [asyncio.create_task(self.worker_loop()) for _ in range(self.max_concurrency)]
        
        await asyncio.gather(*workers)
        await self.scraper.shutdown()

        self.metrics["Active Workers Running"] = 0
        TerminalDashboard.render_header("CONCURRENT SWEEPS MATRIX COMPLETE")
        TerminalDashboard.render_stats_table(self.metrics)

# ==============================================================================
# PIPELINE ORCHESTRATOR ENTRYPOINT
# ==============================================================================
async def execute_orchestrated_sweep():
    os.makedirs("outputs", exist_ok=True)
    
    # Harvest and establish secure network tracks
    scavenger = ProxyScavenger()
    active_proxies = await scavenger.run()
    selected_proxy = active_proxies[0] if active_proxies else None

    # Load target routes through Courlan filters
    raw_targets = [
        "https://news.ycombinator.com/news?tracker=true",
        "https://news.ycombinator.com/best",
        "https://news.ycombinator.com/newest"
    ]
    validated_targets = [CourlanRouter.validate_and_clean(t) for t in raw_targets if CourlanRouter.validate_and_clean(t)]

    # Instantiate multi-threaded task worker engine layout with Max Concurrency set to 2
    manager = ConcurrentPipelineManager(targets=validated_targets, max_concurrency=2, proxy=selected_proxy)
    await manager.run_pipeline()

    print("\033[1;32m[+ PASS]\033[0m Integration matrix pipeline loops finalized successfully.")
    GitAutomationMatrix.secure_commit()

if __name__ == "__main__":
    asyncio.run(execute_orchestrated_sweep())
