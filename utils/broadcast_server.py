import os
import sys
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# Force parent folder scope resolution to handle standalone shell calls cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.shared_memory import iter_workers

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BroadcastServer")

CLUSTER_STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
MIN_RETRY_AFTER = 1
MAX_RETRY_AFTER = 300

class BackpressureHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _get_standard_lane_depth(self):
        if CLUSTER_STATE_FILE.exists():
            try:
                with open(CLUSTER_STATE_FILE, 'r') as f:
                    data = json.load(f)
                diagnostics = data.get("worker_diagnostics", {})
                return sum(stats.get("standard_lane_depth", 0) for stats in diagnostics.values())
            except:
                pass
        return 0

    def _calculate_retry_after(self, std_lane_depth: int) -> int:
        total_rate = sum(rate for _, rate, online in iter_workers() if online)
        if total_rate <= 0:
            total_rate = 35.0  # Production engineering fallback baseline

        wait = int(std_lane_depth / total_rate)
        return max(MIN_RETRY_AFTER, min(MAX_RETRY_AFTER, wait))

    def do_POST(self):
        std_lane_depth = self._get_standard_lane_depth()
        is_priority = self.headers.get("X-Priority-Traffic", "false").lower() == "true"
        
        if std_lane_depth >= 1200:
            global_action = "SHED_LOAD"
        else:
            global_action = "NOMINAL"

        if global_action == "SHED_LOAD":
            if is_priority:
                self._serve_success()
            else:
                retry_after = self._calculate_retry_after(std_lane_depth)
                self._send_backpressure(global_action, retry_after)
            return

        self._serve_success()

    def _serve_success(self):
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ACCEPTED", "message": "Payload queued for lane execution."}')

    def _send_backpressure(self, reason, retry_after):
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        
        response = {
            "status": "REJECTED",
            "reason": reason,
            "suggested_backoff_seconds": retry_after
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, BackpressureHTTPHandler)
    logger.info(f"🚀 Weighted Ingress Engine active on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run_server()
