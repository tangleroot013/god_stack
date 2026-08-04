#!/usr/bin/env python3
import http.server
import threading
import logging

logger = logging.getLogger("TelemetryExporter")

# Shared atomic telemetry tracking structure
SYSTEM_METRICS = {
    "god_stack_ingestion_attempts_total": 0,
    "god_stack_ingestion_success_total": 0,
    "god_stack_deduplication_skips_total": 0,
    "god_stack_bytes_processed_total": 0,
    "nodes_processed_total": 0,
    "nodes_quarantined_total": 0,
    "buffer_fill_ratio": 0.0
}

class TelemetryMetricWrapper:
    def __init__(self, key: str):
        self.key = key

    def labels(self, *args, **kwargs):
        """Intercepts Prometheus dimension tags natively and returns self for chaining."""
        return self

    def inc(self, amount: int = 1):
        SYSTEM_METRICS[self.key] += amount

    def set(self, value: float):
        SYSTEM_METRICS[self.key] = value

# Exported API matching expectations in god_scraper.py with fluent interface support
NODES_PROCESSED = TelemetryMetricWrapper("nodes_processed_total")
NODES_QUARANTINED = TelemetryMetricWrapper("nodes_quarantined_total")
BUFFER_FILL = TelemetryMetricWrapper("buffer_fill_ratio")

class PrometheusMetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            
            output = []
            for metric_name, val in SYSTEM_METRICS.items():
                metric_type = "gauge" if "ratio" in metric_name else "counter"
                output.append(f"# TYPE {metric_name} {metric_type}")
                output.append(f"{metric_name} {val}")
            
            self.wfile.write("\n".join(output).encode("utf-8") + b"\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def start_metrics_server(port: int = 8000):
    """Spins up the scraper exposition server context (expected by test suites)."""
    server = http.server.HTTPServer(("0.0.0.0", port), PrometheusMetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"📊 Telemetry Edge live and exporting metrics on port :{port}/metrics")

# Maintain backward compatibility alias
start_telemetry_server = start_metrics_server

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    start_metrics_server(8000)
    import time
    print("Self-testing telemetry matrix server loop... Control+C to terminate.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping diagnostic line.")
