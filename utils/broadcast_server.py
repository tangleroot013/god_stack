import sys
import os
import asyncio
import logging
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.search_ledger import SearchLedger
from utils.latency_telemetry import LatencyTelemetry
from utils.binary_processor import WorkerBinaryProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("UnifiedDaemon")

STATE_FILE = ROOT_DIR / "vaults" / "cluster_state.json"
ROUTING_MAP_FILE = ROOT_DIR / "vaults" / "optimized_routing.json"

class BackpressureHTTPHandler(SimpleHTTPRequestHandler):
    def calculate_dynamic_backoff(self):
        """Calculates expected clearance windows using total unified backlogs."""
        default_delay = 10
        if not STATE_FILE.exists():
            return default_delay
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            diagnostics = state.get("worker_diagnostics", {})
            max_queue = 0
            for worker, stats in diagnostics.items():
                max_queue = max(max_queue, stats.get("queue_depth", 0))
            return max(5, min(60, int(max_queue / 50)))
        except:
            return default_delay

    def do_GET(self):
        """Maintains strict prioritized route isolation."""
        telemetry_whitelist = ["/api/health", "/index.html", "/cluster_state.json", "/favicon.ico"]
        
        if ROUTING_MAP_FILE.exists():
            try:
                with open(ROUTING_MAP_FILE, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                
                if rules.get("global_action") == "THROTTLE_INGESTION":
                    if self.path not in telemetry_whitelist and not self.path.startswith("/dist/"):
                        priority_token = self.headers.get("X-Priority", "Standard")
                        
                        if priority_token == "High":
                            logger.warning(f"⚡ FAST PATH ENGAGED: High-priority task channeled directly to head of processing queue on: {self.path}")
                        else:
                            retry_seconds = self.calculate_dynamic_backoff()
                            self.send_response(503)
                            self.send_header("Content-Type", "application/json")
                            self.send_header("Retry-After", str(retry_seconds))
                            self.end_headers()
                            
                            response = {
                                "error": "QUEUE_DEGRADED", 
                                "message": "Standard ingestion lanes blocked. Core queue partitioning active.",
                                "retry_after_seconds": retry_seconds
                            }
                            self.wfile.write(json.dumps(response).encode())
                            return
            except Exception as e:
                logger.error(f"Failed to execute partitioned backpressure logic: {e}")

        super().do_GET()

class LiveWatcher:
    def __init__(self):
        self.vaults_dir = ROOT_DIR / "vaults"
        self.watch_dir = self.vaults_dir / "intelligence_graph"
        self.state_file = self.vaults_dir / "cluster_state.json"
        
        self.ledger = SearchLedger(vault_path=str(self.watch_dir))
        self.telemetry = LatencyTelemetry()
        self.bin_processor = WorkerBinaryProcessor()

    async def watch_loop(self):
        logger.info(f"📡 Multi-vector engine spinning. Emitting to: {self.state_file}")
        while True:
            current_graph = self.ledger.build_ledger()
            raw_latency = self.telemetry.sample_round_trip()
            
            worker_metrics = {}
            for bin_path in self.vaults_dir.glob("worker_*_telemetry.bin"):
                parsed = self.bin_processor.unpack_payload(bin_path)
                if parsed.get("status") == "VALIDATED":
                    w_id = parsed["worker_id"]
                    worker_metrics[w_id] = {
                        "priority_lane_depth": parsed["priority_queue_depth"],
                        "standard_lane_depth": parsed["standard_queue_depth"],
                        "queue_depth": parsed["queue_depth"],
                        "cpu_util": parsed["cpu_utilization_pct"]
                    }

            unified_state = {
                "timestamp": asyncio.get_event_loop().time(),
                "topology": current_graph,
                "latency_matrix": raw_latency,
                "worker_diagnostics": worker_metrics
            }
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(unified_state, f, indent=4)
                
            signal_file = self.vaults_dir / ".refresh_signal"
            signal_file.write_text(str(unified_state["timestamp"]))
                
            await asyncio.sleep(2)

def run_http_server():
    os.chdir(str(ROOT_DIR / "vaults"))
    handler = BackpressureHTTPHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8090), handler) as httpd:
        logger.info("🖥️ Partitioned Ingestion Gateway running at http://localhost:8090")
        httpd.serve_forever()

if __name__ == "__main__":
    import threading
    
    srv_thread = threading.Thread(target=run_http_server, daemon=True)
    srv_thread.start()
    
    watcher = LiveWatcher()
    try:
        asyncio.run(watcher.watch_loop())
    except KeyboardInterrupt:
        logger.info("👋 Unified broadcast daemon shut down cleanly.")
