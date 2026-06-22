import asyncio
import random
import json
from utils.queue_manager import RedisQueueManager
from utils.stealth_manager import StealthManager
from utils.log_rotator import get_logger

log = get_logger("RedisWorker")

class RedisWorker:
    """Consumes tasks from Redis and executes missions with progressive retry logic."""
    def __init__(self, worker_id: str, max_retries: int = 3, base_delay: float = 2.0):
        self.worker_id = worker_id
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.stealth = StealthManager()

    async def handle_mission_fault(self, task: dict):
        """Calculates exponential back-off delay and re-queues failed missions."""
        url = task.get('url')
        meta = task.get('meta', {})
        retries = meta.get('retry_count', 0)

        if retries < self.max_retries:
            # Full Jitter Back-off: (base_delay * 2^retries) + random variance
            calculated_delay = (self.base_delay * (2 ** retries)) + random.uniform(0.5, 1.5)
            retries += 1
            meta['retry_count'] = retries
            task['meta'] = meta

            log.warning(f"⚠️ [Worker-{self.worker_id}] Task error on {url}. Retrying in {calculated_delay:.2f}s ({retries}/{self.max_retries})")
            await asyncio.sleep(calculated_delay)

            # Re-queue back to the master pending list
            self.broker.add_target(url, metadata=meta)
            # Evict task from active list now that it is safely duplicated back to pending
            raw_payload = json.dumps(task)
            self.broker.client.lrem(self.broker.active_processing, 1, raw_payload)
            return True
        else:
            log.error(f"❌ [Worker-{self.worker_id}] Max retries exhausted for {url}. Dropping task context.")
            raw_payload = json.dumps(task)
            self.broker.client.lrem(self.broker.active_making, 1, raw_payload)
            return False

    async def run_mission_loop(self):
        log.info(f"🚀 Worker {self.worker_id} ignited. Awaiting targets...")
        while True:
            try:
                task = self.broker.pop_task(timeout=5)
                if task:
                    url = task.get('url')
                    identity = self.stealth.dispatch_identity()
                    log.info(f"⚡ [Worker-{self.worker_id}] Scraping: {url}")

                    # Simulate network exception pathway for failure tracking
                    if "simulate-fault" in url:
                        raise ConnectionError("Simulated infrastructure drop.")

                    # Execution complete
                    self.broker.task_complete(task)
                    log.info(f"✅ Mission Success: {url}")
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                log.error(f"💥 Extraction Fault: {e}")
                if 'task' in locals() and task:
                    await self.handle_mission_fault(task)
            await asyncio.sleep(0.1)
