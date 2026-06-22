import asyncio
import os
import sys
import logging
from utils.stealth_manager import StealthManager
from utils.queue_manager import RedisQueueManager

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[DAEMON-CLUSTER]\033[0m %(message)s")
logger = logging.getLogger("DaemonCore")

class DaemonCore:
    def __init__(self, max_concurrent_workers: int = 3):
        self.stealth = StealthManager()
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        logger.info(f"🚀 G.O.D. Redis Worker Node Active [Capacity: {max_concurrent_workers}]")

    async def run_mission(self, task_data: dict):
        """Executes a single mission within an isolated concurrency slot."""
        async with self.semaphore:
            url = task_data.get('url')
            identity = self.stealth.dispatch_identity()
            ua_mask = identity.get('user_agent', 'Unknown-Agent')

            logger.info(f"⚡ Processing mission: {url} | Masking UA: [{ua_mask}]")

            try:
                # Simulating structural execution block safely for standalone environments
                await asyncio.sleep(0.5) 
                logger.info(f"✅ Mission Successful: {url}")
                self.broker.task_complete(task_data)
            except Exception as e:
                logger.error(f"❌ Mission Fault for {url}: {e}")

    async def main_loop(self):
        """The infinite heartbeat polling the memory-resident task queue broker."""
        logger.info("🤖 Awaiting matrix cycles from Redis broker...")
        while True:
            try:
                # Reliable atomic pop from pending state queue registers
                task = self.broker.pop_task(timeout=2)
                if task:
                    asyncio.create_task(self.run_mission(task))
                else:
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Broker connection drop or internal fault: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    core = DaemonCore(max_concurrent_workers=5)
    try:
        asyncio.run(core.main_loop())
    except KeyboardInterrupt:
        print("\n🛑 Stopping G.O.D. Worker Node cleanly.")
