#!/usr/bin/env python3
# ==============================================================================
# G.O.D. TELEMETRY EXPORTER (metrics_exporter.py)
# Architecture: FOSS-compliant inline exposition endpoint for Prometheus targets.
# ==============================================================================
import http.server
import threading
import logging
import socket
from config import METRICS_PORT

logger = logging.getLogger("TelemetryExporter")

# Shared atomic telemetry counters
SYSTEM_METRICS = {
    "god_stack_ingestion_attempts_total": 0,
    "god_stack_ingestion_success_total": 0,
    "god_stack_deduplication_skips_total": 0,
    "god_stack_bytes_processed_total": 0,
    "god_stack_active_daemons": 0
}

class ResilientHTTPServer(http.server.HTTPServer):
    """Overrides socket parameters to clear TIME_WAIT locks and allow instant restarts."""
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        super().server_bind()

class PrometheusMetricsHandler(http.server.BaseHTTPRequestHandler):
    """Exposes real-time state metrics using standard OpenMetrics format."""
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            
            output = []
            for metric_name, val in SYSTEM_METRICS.items():
                output.append(f"# TYPE {metric_name} counter")
                output.append(f"{metric_name} {val}")
            
            self.wfile.write("\n".join(output).encode("utf-8") + b"\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence standard HTTP server poll text to protect console clarity
        pass

# Global execution lock to prevent duplicate binding sequences within the same process thread array
_server_lock = threading.Lock()
_server_started = False

def start_telemetry_server(port: int = None):
    """Spins up the scraper exposition server context safely inside a singleton wrapper."""
    global _server_started
    target_port = port if port is not None else METRICS_PORT
    
    with _server_lock:
        if _server_started:
            return
        try:
            server = ResilientHTTPServer(("0.0.0.0", target_port), PrometheusMetricsHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            _server_started = True
            logger.info(f"📊 Telemetry Edge live and exporting metrics on port :{target_port}/metrics")
        except OSError as e:
            logger.warning(f"Network intercept: Target port :{target_port} handled or active elsewhere. Thread bypassing safely. Details: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    start_telemetry_server(METRICS_PORT)
    import time
    print("Self-testing telemetry matrix server loop...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
