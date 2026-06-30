#!/usr/bin/env python3
import http.server
import threading
import logging
import sqlite3

logger = logging.getLogger("TelemetryExporter")

DB_PATH = "god_stack_vfs.db"

SYSTEM_METRICS = {
    "god_stack_ingestion_attempts_total": 0,
    "god_stack_ingestion_success_total": 0,
    "god_stack_deduplication_skips_total": 0,
    "god_stack_bytes_processed_total": 0
}

def init_persistent_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize metric database: {e}")

def increment_metric(metric_key: str, val: int = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        cursor.execute("""
            INSERT INTO telemetry (metric_key, metric_value) VALUES (?, ?)
            ON CONFLICT(metric_key) DO UPDATE SET metric_value = metric_value + ?
        """, (metric_key, val, val))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to persist metric mutation: {e}")

def sync_from_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        cursor.execute("SELECT metric_key, metric_value FROM telemetry")
        rows = cursor.fetchall()
        for key, value in rows:
            if key in SYSTEM_METRICS:
                SYSTEM_METRICS[key] = value
        conn.close()
    except Exception:
        pass

class PersistentMetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            sync_from_database()
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
        pass

def start_telemetry_server(port: int = 8089):
    init_persistent_db()
    server = http.server.HTTPServer(("0.0.0.0", port), PersistentMetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"📊 Persistent Telemetry Server operating on port :{port}/metrics")
