import asyncio
import logging
from typing import Callable, Coroutine, Any

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[ENGINE-CRON]\033[0m %(message)s")
logger = logging.getLogger("AsyncScheduler")

class AsyncScheduler:
    """Manages long-running, periodic asynchronous orchestrations at fixed intervals."""
    def __init__(self, interval_seconds: int = 600):
        self.interval = interval_seconds
        self.is_running = False
        self._task = None

    async def _loop(self, job_func: Callable[[], Coroutine[Any, Any, Any]]):
        while self.is_running:
            logger.info("⏰ Interval trigger fired. Initializing target worker batch...")
            try:
                await job_func()
                logger.info("✨ Batch completed successfully. Hibernating context loop.")
            except Exception as e:
                logger.error(f"💥 Critical fault during scheduling execution block: {e}")
            
            await asyncio.sleep(self.interval)

    def start(self, job_func: Callable[[], Coroutine[Any, Any, Any]]):
        """Spins up the daemon background loop thread structure."""
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._loop(job_func))
            logger.info(f"🚀 Periodic core loop registered. Cadence: Every {self.interval}s")

    async def stop(self):
        """Gracefully halts the execution loop and unrolls pending frames."""
        if self.is_running:
            self.is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("🛑 Background scheduling core stopped cleanly.")
