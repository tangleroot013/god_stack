#!/usr/bin/env python3
import time
import os
import sys
import logging
from flask import Flask, jsonify

# Setup direct log streaming
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

app = Flask(__name__)

class MetricsStore:
    def __init__(self):
        self.worker_stats = {}
        self.global_stats = {"processed": 0, "success": 0, "quarantined": 0}
        self.start_time = time.time() 
        self.total_urls = 0

metrics = MetricsStore()

@app.route('/metrics', methods=['GET'])
def get_metrics():
    try:
        app.logger.info("--> Received GET /metrics over Unix Socket")
        elapsed = time.time() - metrics.start_time
        processed = metrics.global_stats.get("processed", 0)
        throughput = processed / elapsed if elapsed > 0 else 0
        eta_secs = (metrics.total_urls - processed) / throughput if throughput > 0 else 0
        
        return jsonify({
            "global": metrics.global_stats,
            "workers": metrics.worker_stats,
            "elapsed_seconds": elapsed,
            "throughput_urls_per_sec": throughput,
            "eta_seconds": eta_secs,
            "total_urls": metrics.total_urls
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    app.logger.info("--> Received GET /health over Unix Socket")
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    app.logger.info("Booting Flask engine over /tmp/metrics.sock...")
    # Corrected parameters for werkzeug's native socket wrapper
    run_simple('unix:///tmp/metrics.sock', 0, app, use_debugger=False, use_reloader=False)
