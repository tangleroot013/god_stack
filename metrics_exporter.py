from prometheus_client import Counter, Gauge, start_http_server

# Labeled Counters
NODES_PROCESSED = Counter(
    "god_stack_nodes_processed_total",
    "Total number of nodes successfully processed and committed",
    ["worker_id"]
)
NODES_QUARANTINED = Counter(
    "god_stack_nodes_quarantined_total",
    "Total number of nodes sent to the dead-letter queue",
    ["worker_id", "error_type"]
)

# Shared Gauges
BUFFER_FILL = Gauge(
    "god_stack_dual_buffer_fill_ratio",
    "Current fill ratio of the primary dual buffer (0-1)"
)

def start_metrics_server(port: int = 8000):
    """Exposes /metrics on the designated network interface."""
    start_http_server(port)
