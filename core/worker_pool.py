import asyncio
import logging
from typing import List
from utils.redis_worker import RedisWorker

class WorkerPool:
    """Orchestrates a cluster of concurrent worker nodes with fault recovery."""
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.workers: List[RedisWorker] = []
        self.logger = logging.getLogger("WorkerPool")
        self._running = False

    async def start_pool(self):
        """Ignites the worker cluster and maintains operational depth."""
        self._running = True
        self.logger.info(f"🔥 Igniting Worker Pool [Size: {self.pool_size}]")
        
        # Initialize the worker instances
        tasks = []
        for i in range(self.pool_size):
            worker = RedisWorker(worker_id=f"Node-{i:02d}")
            self.workers.append(worker)
            # Each worker runs in its own non-blocking task
            tasks.append(asyncio.create_task(worker.run_mission_loop()))
        
        # Monitor the task group
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"❌ Pool Integrity Fault: {e}")
        finally:
            self.running = False

    def stop_pool(self):
        """Safely signals the pool to spin down."""
        self._running = False
        self.logger.warning("🛑 Pool shutdown sequence initiated.")
