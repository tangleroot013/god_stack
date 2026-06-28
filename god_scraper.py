import asyncio
import logging
from typing import List, Optional, Union, Any
from frontier_manager import Frontier
from god_engine import GodEngineNode

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[GOD-SCRAPER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, concurrency_limit: int = 10, headless: bool = True, proxy_url: Optional[str] = None, profile_name: Optional[str] = None, **kwargs):
        self.concurrency_limit = concurrency_limit
        self.headless = headless
        self.proxy_url = proxy_url
        self.profile_name = profile_name
        self.context: Any = None
        self.concurrency_limit = concurrency_limit
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.active = False

    async def initialize(self):
        """Prepares worker matrices and underlying extraction dependencies."""
        logger.info("Initializing unified scraping engine runner sequence...")
        await GodEngineNode.initialize(headless=True)
        self.active = True
        logger.info(f"Scraper sequence active. Concurrency ceiling set to: {self.concurrency_limit}")

    async def process_target(self, url: str):
        """Handles an isolated route extraction cycle with structural rate bounds."""
        async with self.semaphore:
            if not self.active:
                return

            try:
                result = await GodEngineNode.fetch_and_extract(url)
                
                if result["status"] == "SUCCESS":
                    discovered_links = result["extracted_data"]["links"]
                    if discovered_links:
                        logger.info(f"Discovered {len(discovered_links)} outbound routes from {url}. Enqueuing to Frontier...")
                        # Handle either batch or singular fallback dynamically
                        if hasattr(Frontier, 'enqueue_batch'):
                            Frontier.enqueue_batch(discovered_links)
                        elif hasattr(Frontier, 'enqueue'):
                            for link in discovered_links:
                                Frontier.enqueue(link)
                else:
                    logger.warning(f"Target route resolution returned explicit abort state: {result['status']} for {url}")

            except Exception as e:
                logger.error(f"Critical processing violation encountered across hotpath {url}: {str(e)}")

    def _get_next_targets(self, batch_size: int = 5) -> List[str]:
        """Dynamically captures active targets from available Frontier methods."""
        # 1. Batched method variant
        if hasattr(Frontier, 'dequeue_batch'):
            return Frontier.dequeue_batch(batch_size=batch_size)
        
        # 2. Singular variant fallbacks
        targets = []
        for method_name in ['dequeue', 'get', 'pop']:
            if hasattr(Frontier, method_name):
                method = getattr(Frontier, method_name)
                for _ in range(batch_size):
                    try:
                        # Attempt execution handling properties
                        res = method()
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

    
    async def scrape(self, urls: Union[str, List[str]]) -> Any:
        """Compatibility layer for test orchestrators invoking batch URLs."""
        if isinstance(urls, str):
            return await self.process_target(urls)
        return [await self.process_target(u) for u in urls]

    async def shutdown(self):
        """Terminates engine tasks and cleans workspace pipeline states."""
        logger.info("Executing graceful scraper teardown sequence...")
        self.active = False
        await GodEngineNode.shutdown()
        logger.info("Scraper core subsystem deactivated successfully.")

# Global production singleton scraper deployment node
GodScraperNode = GodScraper()
