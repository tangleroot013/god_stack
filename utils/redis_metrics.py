import redis
import logging
import asyncio
from utils.monitor_relay import MonitorRelay

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;36m[REDIS-METRICS]\033[0m %(message)s")
logger = logging.getLogger("RedisMetrics")

class RedisMetricsExporter:
    """Polls Redis task state and exports telemetry to the live dashboard."""
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.pending_key = "god_stack:tasks:pending"
        self.active_key = "god_stack:tasks:active"
        self.seen_key = "god_stack:tasks:seen"

    async def broadcast_cycle(self, relay: MonitorRelay):
        """Extracts atomic counts and streams them to the WebSocket relay."""
        try:
            metrics = {
                "pending_tasks": self.client.llen(self.pending_key),
                "active_workers": self.client.llen(self.active_key),
                "total_mapped": self.client.scard(self.seen_key)
            }
            # Unified broadcast token matching frontend expectation loops
            await relay.broadcast("redis_telemetry", metrics)
            logger.debug(f"📊 Broadcasted Redis metrics -> Pending: {metrics['pending_tasks']}")
        except Exception as e:
            logger.error(f"❌ Metrics Export Fault: {e}")
