import redis
import logging
import json
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[REDIS-BROKER]\033[0m %(message)s")
logger = logging.getLogger("QueueManager")

class RedisQueueManager:
    """Memory-resident broker utilizing BRPOPLPUSH for reliable multi-node scaling."""
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pending_queue = "god_stack:tasks:pending"
        self.active_processing = "god_stack:tasks:active"
        self.seen_set = "god_stack:tasks:seen"

    def add_target(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Atomically deduplicates using a Redis Set and appends to the FIFO queue."""
        if self.client.sadd(self.seen_set, url):
            payload = json.dumps({"url": url, "meta": metadata or {}})
            self.client.rpush(self.pending_queue, payload)
            logger.info(f"📥 Mission queued: {url}")
            return True
        return False

    def pop_task(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Reliably pops a task from pending to active using BRPOPLPUSH.
        Preserves tasks in the processing register if a worker terminates mid-flight.
        """
        task_data = self.client.brpoplpush(self.pending_queue, self.active_processing, timeout=timeout)
        if task_data:
            return json.loads(task_data)
        return None

    def task_complete(self, task_payload: Dict[str, Any]):
        """Acknowledges task completion by removing its payload from the active registry."""
        raw_payload = json.dumps(task_payload)
        # Remove exactly 1 matching element from the active working ledger
        removed = self.client.lrem(self.active_processing, 1, raw_payload)
        if removed > 0:
            logger.info(f"✅ Mission finalized: {task_payload.get('url')}")
        return bool(removed)
