import datetime
import logging
from utils.monitor_relay import MonitorRelay

logger = logging.getLogger("DaemonCore")

class DaemonCore:
    def __init__(self, monitor_relay: MonitorRelay = None):
        self.monitor = monitor_relay or MonitorRelay()

    async def run_job(self, name: str, coro) -> dict:
        """Executes a scrapers workflow task and hooks telemetry states to the relay."""
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        await self.monitor.broadcast("worker_start", {"worker": name, "timestamp": timestamp})

        try:
            result = await coro
            await self.monitor.broadcast("worker_success", {"worker": name, "status": "200 OK", "data": result})
            return {"status": "completed", "worker": name}
        except Exception as e:
            await self.monitor.broadcast("worker_fault", {"worker": name, "error": str(e)})
            return {"status": "failed", "worker": name, "error": str(e)}
