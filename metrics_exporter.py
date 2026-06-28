#!/usr/bin/env python3
import http.server
import threading
import logging
import socket

logger = logging.getLogger("TelemetryExporter")

# Shared atomic telemetry counters
SYSTEM_METRICS = {
    "god_stack_ingestion_attempts_total": 0,
    "god_stack_ingestion_success_total": 0,
    "god_stack_deduplication_skips_total": 0,
    "god_stack_bytes_processed_total": 0
}

class ResilientHTTPServer(http.server.HTTPServer):
    def server_bind(self):
        # Enforces local SO_REUSEADDR configurations to protect ports against TCP TIME_WAIT locks
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
        # Suppress request polling logging for clean trace outputs
        pass

def start_telemetry_server(port: int = 8000):
    """Spins up the scraper exposition server context in a background thread."""
    server = ResilientHTTPServer(("0.0.0.0", port), PrometheusMetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"📊 Telemetry Edge live and exporting metrics on port :{port}/metrics")
    return server
