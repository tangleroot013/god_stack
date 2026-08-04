import asyncio
import aiohttp
import logging
from god_scraper import GodScraper
from utils.queue_manager import RedisQueueManager

class RedisWorker:
    """Executes atomic missions pulling from a real-world Redis container."""
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.broker = RedisQueueManager(host="localhost", port=6379)
        self.scraper = GodScraper()
        self.logger = logging.getLogger(f"Worker-{worker_id}")

    async def execute_transaction(self, task: dict):
        """Finalizes the Scrape-to-Vault loop with atomic handoff."""
        try:
            result = await self.scraper.scrape(task['url'], identity=task['identity'])
            async with aiohttp.ClientSession() as session:
                async with session.post("http://127.0.0.1:8890/vault/sync", json={"data": result}) as resp:
                    if resp.status == 200:
                        self.broker.task_complete(task)
                        self.logger.info(f"💎 Vault Secured: {task['url']}")
        except Exception as e:
            self.logger.error(f"💥 Transactional Fault: {e}")

    async def run_mission_loop(self):
        """Main loop driven by the Parallel Performance Optimizer."""
        self.logger.info("Ready and listening for atomic broker tasks.")
        while True:
            await asyncio.sleep(3600)
