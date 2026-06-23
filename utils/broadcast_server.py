import json
import logging
import mmap
import struct
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BroadcastServer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHM_FILE = PROJECT_ROOT / "vaults" / ".routing_matrix.shm"

MIN_RETRY_AFTER = 1
MAX_RETRY_AFTER = 60

class BackpressureHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def _read_shm_matrix(self):
        """Reads the dynamic cluster state directly from shared memory with zero disk I/O."""
        if not SHM_FILE.exists():
            return "NOMINAL", 50.0, 0
        
        try:
            with open(SHM_FILE, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Layout: 12s (action), d (drain_rate), d (timestamp), I (std_lane_depth)
                    packed_data = mm[0:32]
                    action_bytes, drain_rate, _, std_lane_depth = struct.unpack("<12sddI", packed_data)
                    global_action = action_bytes.decode('utf-8').strip('\x00')
                    return global_action, drain_rate, std_lane_depth
        except Exception as e:
            # Safe internal fallback under memory access errors
            return "NOMINAL", 50.0, 0

    def do_POST(self):
        state, worker_ema_drain, std_lane_depth = self._read_shm_matrix()
        is_priority = self.headers.get("X-Priority-Traffic", "false").lower() == "true"

        if state == "THROTTLE_INGESTION":
            self._apply_backpressure(state, worker_ema_drain, std_lane_depth, priority_breach=True)
            return
        elif state == "SHED_LOAD":
            if is_priority:
                self._serve_success()
            else:
                self._apply_backpressure(state, worker_ema_drain, std_lane_depth, priority_breach=False)
            return

        self._serve_success()

    def _serve_success(self):
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "ACCEPTED", "message": "Payload queued for memory lane."}')

    def _apply_backpressure(self, state, drain_rate, depth, priority_breach=False):
        retry_after = 5
        
        if not priority_breach and drain_rate > 0:
            calculated_wait = int(depth / drain_rate)
            retry_after = min(MAX_RETRY_AFTER, max(MIN_RETRY_AFTER, calculated_wait))
        elif priority_breach:
            retry_after = 30

        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Retry-After", str(retry_after))
        self.end_headers()
        
        response_body = {
            "status": "REJECTED",
            "reason": state,
            "suggested_backoff_seconds": retry_after
        }
        self.wfile.write(json.dumps(response_body).encode('utf-8'))

def run_server(port=8090):
    server_address = ('', port)
    httpd = HTTPServer(server_address, BackpressureHTTPHandler)
    logger.info(f"🚀 Memory-Resident Ingestion Engine active on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run_server()
