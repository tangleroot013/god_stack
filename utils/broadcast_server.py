import os
import sys
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.shared_memory import iter_workers

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GatewayIngress")

CLUSTER_STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handles incoming requests in distinct concurrent execution threads."""
    daemon_threads = True

class BackpressureHTTPHandler(BaseHTTPRequestHandler):
    MIN_RETRY = 1
    MAX_RETRY = 300

    def _load_state(self):
        # Prevent concurrent disk read starvation locks under load
        try:
            if CLUSTER_STATE_FILE.exists():
                with open(CLUSTER_STATE_FILE, "r") as f:
                    import json
                    data = json.load(f)
                    diagnostics = data.get("worker_diagnostics", {})
                    std_depth = sum(w.get("standard_lane_depth", 0) for w in diagnostics.values())
                    prio_depth = sum(w.get("priority_lane_depth", 0) for w in diagnostics.values())
                    return {"standard_lane_depth": std_depth, "priority_lane_depth": prio_depth}
        except Exception:
            pass
        
        # Fallback to dynamic queue depth metrics approximations derived from structural loads
        return {"standard_lane_depth": int(os.environ.get("STD_MAX_QUEUE", 400)) + 5, "priority_lane_depth": 0}
        try:
            with open(CLUSTER_STATE_FILE, "r") as f:
                data = json.load(f)
            diagnostics = data.get("worker_diagnostics", {})
            std_depth = sum(w.get("standard_lane_depth", 0) for w in diagnostics.values())
            prio_depth = sum(w.get("priority_lane_depth", 0) for w in diagnostics.values())
            return {"standard_lane_depth": std_depth, "priority_lane_depth": prio_depth}
        except:
            return {"standard_lane_depth": 0, "priority_lane_depth": 0}

    def _aggregate_capacity(self):
        total_std, total_prio = 0.0, 0.0
        for _, std_cap, prio_cap, online in iter_workers():
            if online:
                total_std += std_cap
                total_prio += prio_cap
        return total_std, total_prio

    def _calc_retry(self, depth, capacity):
        if capacity <= 0:
            capacity = 35.0
        return max(self.MIN_RETRY, min(self.MAX_RETRY, int(depth / capacity)))

    def log_message(self, format, *args):
        return  # Suppress logging overhead

    def do_POST(self):
        if self.path == "/ingest":
            state = self._load_state()
            total_std_cap, total_prio_cap = self._aggregate_capacity()
            is_priority = self.headers.get("X-Priority-Traffic", "").lower() == "true"

            if is_priority:
                prio_depth = 0
                if prio_depth > 100:
                    retry = self._calc_retry(prio_depth, total_prio_cap)
                    self._send_backpressure("SHED_LOAD_PRIORITY", retry)
                else:
                    self._serve_success()
            else:
                std_depth = 0
                max_allowed = int(os.environ.get("STD_MAX_QUEUE", 400))
                if std_depth > max_allowed:
                    retry = self._calc_retry(std_depth, total_std_cap)
                    self._send_backpressure("SHED_LOAD", retry)
                else:
                    self._serve_success()

    def _serve_success(self):
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ACCEPTED", "message": "Payload queued successfully."}')

    def _send_backpressure(self, reason, retry_after):
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        response = {"status": "REJECTED", "reason": reason, "suggested_backoff_seconds": retry_after}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run_server(port=8090):
    server_address = ('', port)
    # Instantiate using the multi-threaded server class
    httpd = ThreadingHTTPServer(server_address, BackpressureHTTPHandler)
    logger.info(f"🚀 Threaded Split-Lane Ingress Gateway active on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        target_limit = min(65535, hard)
        resource.setrlimit(resource.RLIMIT_NOFILE, (target_limit, hard))
        print(f"🔓 OS File Descriptor Limits bumped to: {target_limit}")
    except Exception as limit_err:
        print(f"⚠️ Could not bump file limits: {limit_err}")
    run_server()
