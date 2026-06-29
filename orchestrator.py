# ==============================================================================
# G.O.D. STACK ORCHESTRATOR (orchestrator.py)
# Architecture: Unified Pipeline Manager for Sanitize -> Proxy -> Anti-Bot -> Scrape
# ==============================================================================

import asyncio
import logging
from url_sanitizer import UrlSanitizer
from scavenger import ProxyScavenger
from captcha_handler import CaptchaHandler
from god_engine import GodEngine

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;37m[ORCHESTRATOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GodOrchestrator")

class GodOrchestrator:
    def __init__(self, use_proxies: bool = True):
        self.use_proxies = use_proxies
        self.scavenger = ProxyScavenger() if use_proxies else None
        self.sentinel = CaptchaHandler()
        self.engine = GodEngine()
        self.active_proxies = []

    async def initialize_matrix(self):
        """Bootstraps the proxy grid and engine infrastructure layer."""
        if self.use_proxies:
            logger.info("Bootstrapping proxy egress matrix...")
            self.active_proxies = await self.scavenger.run()
        
        # Explicitly stabilize engine processing boundaries
        await self.engine.initialize(headless=True)
        logger.info("Orchestrator matrix initialized and ready.")

    async def execute_mission(self, raw_url: str) -> dict:
        """Runs the full pipeline on a single target with proxy shielding."""
        logger.info(f"Initiating mission for target: {raw_url}")
        
        # Step 1: Sanitize Target
        clean_url = UrlSanitizer.normalize(raw_url)
        if not clean_url:
            return {"status": "error", "message": "Invalid URL structure"}

        # Step 2: Route Selection (Privacy Hardened Egress Node Selection)
        proxy = self.active_proxies[0] if self.active_proxies else None
        
        # Step 3 & 4: Execution (Engine + Captcha Handling)
        logger.info(f"Deploying extraction engine to {clean_url}")
        
        try:
            # Realigned directly to the native async hotpath with proxy injection
            result = await self.engine.fetch_and_extract(clean_url, proxy=proxy)
            return {"status": "success", "target": clean_url, "message": "Data extracted and serialized."}
        except Exception as e:
            logger.error(f"Mission failed: {str(e)}")
            return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    async def run_cli_test():
        print("\n\033[1;32m--- G.O.D. ORCHESTRATOR TERMINAL TEST ---\033[0m")
        orchestrator = GodOrchestrator(use_proxies=False) # Set False for rapid test
        await orchestrator.initialize_matrix()
        await orchestrator.execute_mission("https://news.ycombinator.com/front?utm_source=test")
        await orchestrator.engine.shutdown()
        
    asyncio.run(run_cli_test())
