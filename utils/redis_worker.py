import asyncio
import logging
from utils.queue_manager import RedisQueueManager
from utils.stealth_manager import StealthManager
from utils.log_rotator import get_logger

log = get_logger("RedisWorker")

class RedisWorker:
    """Consumes tasks from centralized Redis queues and coordinates execution loops."""
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.stealth = StealthManager()

    async def run_mission_loop(self):
        log.info(f"🚀 Worker {self.worker_id} ignited. Awaiting targets...")
        while True:
            try:
                task = self.broker.pop_task(timeout=5)
                if task:
                    url = task.get('url')
                    identity = self.stealth.dispatch_identity()
                    log.info(f"⚡ [Worker-{self.worker_id}] Processing: {url} | Mask: [{identity.get('user_agent')}]")

                    # Emulate collection core processing task pass safely
                    await asyncio.sleep(0.2)
                    
                    self.broker.task_complete(task)
                    log.info(f"✅ Mission Success: {url}")
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                log.error(f"❌ Worker cycle fault handling tracking block: {e}")
                await asyncio.sleep(2)
