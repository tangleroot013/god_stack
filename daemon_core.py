import logging
from core.worker_pool import WorkerPool

class DaemonCore:
    def __init__(self, concurrent_slots: int = 5):
        self.logger = logging.getLogger("DaemonCore")
        self.pool = WorkerPool(pool_size=concurrent_slots)
        self.logger.info("⚡ Mainframe Performance Optimizer linked.")

    async def main_loop(self):
        self.logger.info("🤖 G.O.D. Cluster Online. Deploying Pool...")
        
        # The pool now handles task polling and execution management
        await self.pool.start_pool()
