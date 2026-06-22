import asyncio
import signal
import sys
from aiohttp import web
from utils.queue_manager import RedisQueueManager
from utils.log_rotator import get_logger

log = get_logger("DaemonCore")

class DaemonCore:
    def __init__(self, host='0.0.0.0', port=8888, max_concurrent_workers: int = 5):
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.max_workers = max_concurrent_workers
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        self.running = True
        self.host = host
        self.port = port
        
        self.app = web.Application()
        self.app.add_routes([web.get('/healthz', self.health_check)])

    async def health_check(self, request):
        try:
            redis_status = "UP" if self.broker.client.ping() else "DOWN"
        except Exception:
            redis_status = "DOWN"

        data = {
            "status": "NOMINAL" if self.running and redis_status == "UP" else "DEGRADED",
            "redis": redis_status,
            "workers_pooled": self.semaphore._value
        }
        return web.json_response(data)

    def register_signal_listeners(self):
        """Attaches handlers for smooth OS-level process termination."""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self.initiate_shutdown()))
            except NotImplementedError:
                # Fallback for platforms where signal handlers aren't fully implemented in asyncio
                pass

    async def initiate_shutdown(self):
        """Orchestrates sequential task completion before process termination."""
        if not self.running:
            return
            
        log.warning("⚠️ Termination signal caught! Halting consumption and draining worker slots...")
        self.running = False

        # Calculate currently leased async semaphore execution pipelines
        active_slots = self.max_workers - self.semaphore._value
        if active_slots > 0:
            log.info(f"⏳ In-flight tasks discovered. Waiting for {active_slots} slots to clear...")
            while self.semaphore._value < self.max_workers:
                await asyncio.sleep(0.5)

        log.info("🛑 All worker pipelines drained. Mainframe powering down cleanly.")
        sys.exit(0)

    async def main_loop(self):
        """Main loop managing application lifecycles and registration."""
        self.register_signal_listeners()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        log.info(f"🏥 Diagnostics listener active at http://{self.host}:{self.port}/healthz")

        while self.running:
            try:
                task = self.broker.pop_task(timeout=2)
                if task:
                    # Non-blocking async execution handler
                    asyncio.create_task(self._dummy_worker_slot(task))
                else:
                    await asyncio.sleep(0.5)
            except Exception as e:
                if self.running:
                    log.error(f"Polling loop exception: {e}")
                    await asyncio.sleep(2)

    async def _dummy_worker_slot(self, task: dict):
        async with self.semaphore:
            log.info(f"⚡ Execution start: {task.get('url')}")
            await asyncio.sleep(0.5)
            self.broker.task_complete(task)

if __name__ == "__main__":
    core = DaemonCore()
    try:
        asyncio.run(core.main_loop())
    except KeyboardInterrupt:
        pass
