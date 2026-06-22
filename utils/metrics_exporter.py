import time
from prometheus_client import start_http_server, Counter, Gauge, Summary
from utils.log_rotator import get_logger

log = get_logger("MetricsExporter")

# Define the G.O.D. Stack Metric Registry Metrics
JOBS_PROCESSED = Counter('god_stack_jobs_total', 'Total tasks processed by cluster', ['status'])
ACTIVE_WORKERS = Gauge('god_stack_active_workers', 'Current active concurrent worker count')
REDIS_LATENCY = Summary('god_stack_redis_ping_seconds', 'Redis cluster connection latency')

class MetricsExporter:
    """Exposes standard telemetry formats for time-series scraper collections."""
    def __init__(self, port=9090):
        self.port = port
        self._initialized = False

    def start(self):
        """Starts the local HTTP metric server."""
        if not self._initialized:
            start_http_server(self.port)
            log.info(f"📊 Prometheus metrics endpoint live at http://localhost:{self.port}/metrics")
            self._initialized = True

    def record_job(self, success: bool = True):
        """Increments job completion statuses atomically."""
        status_label = "success" if success else "fault"
        JOBS_PROCESSED.labels(status=status_label).inc()

    def update_worker_count(self, count: int):
        """Updates the active execution thread registry count."""
        ACTIVE_WORKERS.set(count)

    def measure_redis(self, redis_client):
        """Measures and updates Redis network round-trip performance."""
        start_time = time.time()
        try:
            if redis_client.ping():
                REDIS_LATENCY.observe(time.time() - start_time)
        except Exception as e:
            log.error(f"Failed to record broker round-trip latency metrics: {e}")
