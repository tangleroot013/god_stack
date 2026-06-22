import time
from prometheus_client import start_http_server, Counter, Gauge, Summary
from utils.log_rotator import get_logger

log = get_logger("MetricsExporter")

# Core telemetry registries
JOBS_PROCESSED = Counter('god_stack_jobs_total', 'Total tasks processed by cluster', ['status'])
ACTIVE_WORKERS = Gauge('god_stack_active_workers', 'Current active concurrent worker count')
REDIS_LATENCY = Summary('god_stack_redis_ping_seconds', 'Redis cluster connection latency')

# Expanded error vector tracking matrix
ERROR_RATIO = Counter(
    'god_stack_error_ratio', 
    'Error occurrences categorized by functional subsystem source', 
    ['type']
)

class MetricsExporter:
    """Exposes structured multidimensional telemetry formats for Prometheus scraping."""
    def __init__(self, port=9090):
        self.port = port
        self._initialized = False

    def start(self):
        """Starts the local HTTP metric server endpoints safely."""
        if not self._initialized:
            start_http_server(self.port)
            log.info(f"📊 Expanded metrics endpoint live at http://localhost:{self.port}/metrics")
            self._initialized = True

    def record_job(self, success: bool = True):
        status_label = "success" if success else "fault"
        JOBS_PROCESSED.labels(status=status_label).inc()

    def record_error(self, error_type: str):
        """Increments error counts matching a specific string classification label."""
        # Standardized categorizations: 'timeout' | 'parse' | 'network' | 'auth'
        ERROR_RATIO.labels(type=error_type).inc()

    def update_worker_count(self, count: int):
        ACTIVE_WORKERS.set(count)

    def measure_redis(self, redis_client):
        start_time = time.time()
        try:
            if redis_client.ping():
                REDIS_LATENCY.observe(time.time() - start_time)
        except Exception as e:
            log.error(f"Failed to record broker latency: {e}")
            self.record_error("network")
