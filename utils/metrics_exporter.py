import asyncio
import logging
from utils.queue_manager import RedisQueueManager
from utils.monitor_relay import MonitorRelay

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;36m[METRICS-EXP]\033[0m %(message)s")
logger = logging.getLogger("MetricsExporter")

class MetricsExporter:
    """Periodically queries Redis queue metadata and transmits it to the MonitorRelay."""
    def __init__(self, broker: RedisQueueManager, relay: MonitorRelay, check_interval: int = 2):
        self.broker = broker
        self.relay = relay
        self.interval = check_interval
        self.is_running = False
        self._task = None

    async def _loop(self):
        while self.is_running:
            try:
                # Query depth and processing metrics inside primitive Redis structures
                pending_depth = self.broker.client.llen(self.broker.pending_queue)
                active_nodes = self.broker.client.llen(self.broker.active_processing)
                total_seen = self.broker.client.scard(self.broker.seen_set)

                # Broadcast data structure payload across the WebSocket ecosystem
                await self.relay.broadcast("cluster_telemetry", {
                    "pending_tasks": pending_depth,
                    "active_workers": active_nodes,
                    "total_discovered": total_seen
                })
                logger.debug(f"📊 Telemetry dispatched -> Pending: {pending_depth} | Active Nodes: {active_nodes}")
            except Exception as e:
                logger.error(f"Failed to compile and transmit queue telemetry: {e}")
            
            await asyncio.sleep(self.interval)

    def start(self):
        """Launches the background reporting loop."""
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._loop())
            logger.info(f"🚀 Telemetry reporting core active (Interval: {self.interval}s)")

    async def stop(self):
        """Halts the metrics tracking task cleanly."""
        if self.is_running:
            self.is_running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("🛑 Telemetry reporting core shutdown verified.")
