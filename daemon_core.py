import asyncio
import sys
from aiohttp import web
from utils.queue_manager import RedisQueueManager
from utils.log_rotator import get_logger

log = get_logger("DaemonCore")

class DaemonCore:
    def __init__(self, host='0.0.0.0', port=8888, max_concurrent_workers: int = 5):
        self.broker = RedisQueueManager(host='localhost', port=6379)
        self.semaphore = asyncio.Semaphore(max_concurrent_workers)
        self.host = host
        self.port = port
        
        self.app = web.Application()
        self.app.add_routes([web.get('/healthz', self.health_check)])

    async def health_check(self, request):
        """Returns the Redis connection status and active worker metrics."""
        try:
            redis_status = "UP" if self.broker.client.ping() else "DOWN"
        except Exception:
            redis_status = "DOWN"

        data = {
            "status": "NOMINAL" if redis_status == "UP" else "DEGRADED",
            "redis": redis_status,
            "workers_pooled": self.semaphore._value
        }
        return web.json_response(data)

    async def start_health_server(self):
        """Spins up the internal health checking HTTP listener."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        log.info(f"🏥 Health-check server active at http://{self.host}:{self.port}/healthz")

    async def main_loop(self):
        await self.start_health_server()
        log.info("🤖 Mainframe Polling Engine initialized and tracking.")
        while True:
            await asyncio.sleep(3600)

if __name__ == "__main__":
    core = DaemonCore()
    try:
        asyncio.run(core.main_loop())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server endpoints cleanly.")
        sys.exit(0)
