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

ROUTING_MAP_FILE = ROOT_DIR / "vaults" / "optimized_routing.json"

class BackpressureHTTPHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        """Provides explicit API mapping alongside network security circuit breakers."""
        # 1. Route API Calls
        if self.path == "/api/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            rules = {"cluster_healthy": True, "global_action": "NOMINAL"}
            if ROUTING_MAP_FILE.exists():
                try:
                    with open(ROUTING_MAP_FILE, 'r', encoding='utf-8') as f:
                        rules = json.load(f)
                except:
                    pass
            self.wfile.write(json.dumps(rules).encode())
            return

        # 2. Enforce Backpressure Circuit Breaker on file ingestion boundaries
        if ROUTING_MAP_FILE.exists():
            try:
                with open(ROUTING_MAP_FILE, 'r', encoding='utf-8') as f:
                    rules = json.load(f)
                
                if rules.get("global_action") == "THROTTLE_INGESTION" and "cluster_state.json" not in self.path:
                    self.send_response(503)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    response = {"error": "CLUSTER_SATURATED", "message": "Backpressure applied. Ingestion halted."}
                    self.wfile.write(json.dumps(response).encode())
                    return
            except Exception as e:
                logger.error(f"Failed to evaluate backpressure rules at gateway: {e}")

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
        logger.info("🖥️ Adaptive Gateway running at http://localhost:8090")
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
