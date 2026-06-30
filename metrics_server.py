#!/usr/bin/env python3
"""
Lightweight HTTP server that exposes concurrent engine metrics.
Called by the dashboard; runs in background or same process.
"""
from flask import Flask, jsonify
from threading import Thread
import time

app = Flask(__name__)

# Global state: updated by concurrent_research_engine
class MetricsStore:
    def __init__(self):
        self.worker_stats = {}
        self.global_stats = {"processed": 0, "success": 0, "quarantined": 0}
        self.start_time = None
        self.total_urls = 0

metrics = MetricsStore()

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Return current pipeline state as JSON."""
    elapsed = (time.time() - metrics.start_time) if metrics.start_time else 0
    throughput = metrics.global_stats["processed"] / elapsed if elapsed > 0 else 0
    eta_secs = (metrics.total_urls - metrics.global_stats["processed"]) / throughput if throughput > 0 else 0
    
    return jsonify({
        "global": metrics.global_stats,
        "workers": metrics.worker_stats,
        "elapsed_seconds": elapsed,
        "throughput_urls_per_sec": throughput,
        "eta_seconds": eta_secs,
        "total_urls": metrics.total_urls
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

def start_server(port=5555):
    """Run Flask in daemon thread."""
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    start_server()
