import asyncio
import sys
from aiohttp import web
from utils.queue_manager import RedisQueueManager
from utils.metrics_exporter import MetricsExporter
from utils.log_rotator import get_logger

log = get_logger("DaemonCore")

class DaemonCore:
    def __init__(self, host='0.0.0.0', port=8888, metrics_port=9090, max_concurrent_workers: int = 5):
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.max_workers = max_concurrent_workers
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        self.running = True
        self.host = host
        self.port = port
        
        # Initialize metrics exporter matrix
        self.metrics = MetricsExporter(port=metrics_port)
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

    async def telemetry_heartbeat_loop(self):
        """Asynchronous worker loop gathering platform gauges continuously."""
        while self.running:
            try:
                self.metrics.measure_redis(self.broker.client)
                active_count = self.max_workers - self.semaphore._value
                self.metrics.update_worker_count(active_count)
            except Exception as e:
                log.error(f"Error compiling instrumentation metric parameters: {e}")
            await asyncio.sleep(5)

    async def main_loop(self):
        self.metrics.start()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        log.info(f"🏥 Diagnostics listener active at http://{self.host}:{self.port}/healthz")

        # Launch the background gauge updater loop cleanly
        asyncio.create_task(self.telemetry_heartbeat_loop())

        while self.running:
            try:
                task = self.broker.pop_task(timeout=2)
                if task:
                    asyncio.create_task(self._execute_slotted_task(task))
                else:
                    await asyncio.sleep(0.5)
            except Exception as e:
                log.error(f"Broker connection drop handled: {e}")
                await asyncio.sleep(2)

    async def _execute_slotted_task(self, task: dict):
        async with self.semaphore:
            log.info(f"⚡ Processing task item: {task.get('url')}")
            try:
                await asyncio.sleep(0.5)
                self.broker.task_complete(task)
                self.metrics.record_job(success=True)
            except Exception:
                self.metrics.record_job(success=False)
