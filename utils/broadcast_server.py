import sys
import os
import asyncio
import logging
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

# Explicitly bind to project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.search_ledger import SearchLedger
from utils.latency_telemetry import LatencyTelemetry
from utils.binary_processor import WorkerBinaryProcessor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("UnifiedDaemon")

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
            # Vector A: Structural Mesh Compilation
            current_graph = self.ledger.build_ledger()
            
            # Vector B: Sample Network Latency
            raw_latency = self.telemetry.sample_round_trip()
            
            # Vector C: Sweep and Parse Worker Binary Payload Dumps
            worker_metrics = {}
            for bin_path in self.vaults_dir.glob("*.bin"):
                parsed = self.bin_processor.unpack_payload(bin_path)
                if parsed.get("status") == "VALIDATED":
                    w_id = parsed["worker_id"]
                    worker_metrics[w_id] = {
                        "queue_depth": parsed["queue_depth"],
                        "cpu_util": parsed["cpu_utilization_pct"]
                    }

            # Compile everything into a unified state payload
            unified_state = {
                "timestamp": asyncio.get_event_loop().time(),
                "topology": current_graph,
                "latency_matrix": raw_latency,
                "worker_diagnostics": worker_metrics
            }
            
            # Atomic export loop
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(unified_state, f, indent=4)
                
            # Pulse the frontend refresh trigger
            signal_file = self.vaults_dir / ".refresh_signal"
            signal_file.write_text(str(unified_state["timestamp"]))
                
            await asyncio.sleep(2)

def run_http_server():
    os.chdir(str(ROOT_DIR / "vaults"))
    handler = SimpleHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8090), handler) as httpd:
        logger.info("🖥️ Retro Web UI server running at http://localhost:8090")
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
