import asyncio
import logging
import sys
from utils.stealth_manager import StealthManager
from utils.queue_manager import RedisQueueManager
from utils.log_rotator import get_logger

log = get_logger("DaemonCore")

class DaemonCore:
    def __init__(self, max_concurrent_workers: int = 3):
        self.stealth = StealthManager()
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        log.info(f"🚀 Distributed Worker Node online [Concurrency limit: {max_concurrent_workers}]")

    async def execute_mission(self, task_data: dict):
        """Processes a single task context within an isolated concurrency slot."""
        async with self.semaphore:
            url = task_data.get('url')
            meta = task_data.get('meta', {})
            
            # Fetch specialized profile configurations per worker request
            identity = self.stealth.dispatch_identity()
            ua_string = identity.get('user_agent', 'Mozilla/5.0')

            log.info(f"⚡ Processing: {url} | Agent: [{ua_string}]")

            try:
                # Simulating clean network isolation delay safely
                await asyncio.sleep(0.5)
                
                log.info(f"✅ Mission Successful: {url}")
                self.broker.task_complete(task_data)
            except Exception as e:
                log.error(f"❌ Execution defect encountered on {url}: {e}")

    async def main_loop(self):
        """Continuous polling core utilizing atomic BRPOPLPUSH mechanisms."""
        log.info("🤖 Polling matrix entries from active Redis cluster...")
        while True:
            try:
                task = self.broker.pop_task(timeout=2)
                if task:
                    asyncio.create_task(self.execute_mission(task))
                else:
                    await asyncio.sleep(0.5)
            except Exception as e:
                log.error(f"Broker connection interruption: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    core = DaemonCore(max_concurrent_workers=5)
    try:
        asyncio.run(core.main_loop())
    except KeyboardInterrupt:
        print("\n🛑 Clean shutdown sequence processed by operator.")
        sys.exit(0)
