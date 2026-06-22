import asyncio
import time
import random
from utils.queue_manager import RedisQueueManager
from utils.stealth_manager import StealthManager
from utils.log_rotator import get_logger

log = get_logger("RedisWorker")

class RedisWorker:
    """Independent cluster worker that executes discrete target tasks with back-off retry logic."""
    def __init__(self, worker_id: str, max_retries: int = 3, base_backoff: float = 2.0):
        self.worker_id = worker_id
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.stealth = StealthManager()
        self.max_retries = max_retries
        self.base_backoff = base_backoff

    async def execute_with_retry(self, task_data: dict) -> bool:
        """Executes processing tasks using an exponential back-off strategy for isolation defects."""
        url = task_data.get("url")
        meta = task_data.get("meta", {})
        retries = meta.get("retry_count", 0)

        identity = self.stealth.dispatch_identity()
        
        try:
            log.info(f"👷 [Worker {self.worker_id}] Processing: {url} (Attempt {retries + 1}/{self.max_retries + 1})")
            
            # Simulate underlying scraping engine execution bounds
            await asyncio.sleep(0.2)
            
            # Simulated strict validation check for handling error test pathways
            if "fail-target" in url:
                raise ConnectionError("Network fingerprint mismatch or server drop.")

            log.info(f"✅ [Worker {self.worker_id}] Task completed cleanly: {url}")
            self.broker.task_complete(task_data)
            return True

        except Exception as e:
            log.error(f"⚠️ [Worker {self.worker_id}] Execution error on {url}: {e}")
            
            if retries < self.max_retries:
                meta["retry_count"] = retries + 1
                task_data["meta"] = meta
                
                # Calculate randomized exponential sleep delay: base * 2^retry + jitter
                sleep_duration = (self.base_backoff * (2 ** retries)) + random.uniform(0.5, 1.5)
                log.warning(f"🔄 Retrying {url} in {sleep_duration:.2f}s...")
                
                await asyncio.sleep(sleep_duration)
                # Re-queue back to the primary list to support dynamic worker balancing
                self.broker.add_target(url, metadata=meta)
                # Clear processing track footprint safely
                self.broker.client.lrem(self.broker.active_processing, 1, json.dumps(task_data))
            else:
                log.error(f"❌ [Worker {self.worker_id}] Critical failure: Max retries exhausted for {url}")
                self.broker.client.lrem(self.broker.active_processing, 1, json.dumps(task_data))
            return False
