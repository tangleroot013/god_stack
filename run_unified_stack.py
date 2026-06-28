import asyncio
import logging
from frontier_manager import Frontier
from url_sanitizer import UrlSanitizer
from scavenger import ProxyScavenger
from god_scraper import GodScraper

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[MATRIX-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixCore")

class UnifiedExecutionMatrix:
    def __init__(self, target_urls: list):
        self.shutdown_event = asyncio.Event()
        self.sanitized_urls = []
        self.raw_urls = target_urls
        self.scavenger = ProxyScavenger()
        self.engine = GodScraper()

    async def run_url_sanitizer_layer(self):
        logger.info("[SANITIZER] Initializing structural target validation matrix...")
        valid_pool = []
        for url in self.raw_urls:
            normalized = UrlSanitizer.normalize(url)
            if normalized:
                valid_pool.append(normalized)
        self.sanitized_urls = valid_pool
        
        Frontier.enqueue_batch(self.sanitized_urls)
        logger.info(f"[SANITIZER] Target alignment complete. Secured {len(self.sanitized_urls)} production routes.")

    async def bootstrap(self):
        await self.run_url_sanitizer_layer()
        proxies = await self.scavenger.run()
        await self.engine.initialize(headless=True)

        while not self.shutdown_event.is_set():
            url = Frontier.dequeue()
            if not url:
                logger.info("Frontier target queues depleted. Pausing runtime loops.")
                break
                
            logger.info(f"[ENGINE] Firing extraction matrix sequences across active hotpaths for: {url}")
            stats = Frontier.stats()
            logger.info(f"[METRICS] Live Stats Matrix Queue Depth: {stats['queue_depth']} | Dequeue Operations: {stats['frontier.dequeue']}")
            
            await asyncio.sleep(0.1)

        await self.teardown()

    async def teardown(self):
        logger.info("Closing active tasks and tearing down network context structures...")
        await self.engine.shutdown()
        logger.info("[SUCCESS] Refactor matrix lifecycle execution complete. Workspace clean.")

async def main():
    test_urls = ["NEWS.YCOMBINATOR.COM/newest", "https://news.ycombinator.com/best"]
    matrix = UnifiedExecutionMatrix(test_urls)
    await matrix.bootstrap()

if __name__ == "__main__":
    asyncio.run(main())
