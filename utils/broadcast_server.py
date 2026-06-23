import sys
import os
import asyncio
import logging
import json
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

# Anchor explicitly to project root context
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.search_ledger import SearchLedger
from utils.latency_telemetry import LatencyTelemetry

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BroadcastDaemon")

class LiveWatcher:
    def __init__(self):
        self.watch_dir = ROOT_DIR / "vaults" / "intelligence_graph"
        self.matrix_file = ROOT_DIR / "vaults" / "matrix_map.json"
        self.telemetry_file = ROOT_DIR / "vaults" / "telemetry_map.json"
        
        self.ledger = SearchLedger(vault_path=str(self.watch_dir))
        self.telemetry = LatencyTelemetry()
        self.last_graph_state = None

    async def watch_loop(self):
        logger.info(f"📡 Multi-vector monitor active. Targeting paths under: {ROOT_DIR / 'vaults'}")
        while True:
            # Vector A: Track structural vault file changes
            current_graph = self.ledger.build_ledger()
            if self.last_graph_state is None or current_graph != self.last_graph_state:
                logger.info("🔄 Graph structural change detected! Syncing matrix map...")
                self.ledger.export_matrix(output_file=str(self.matrix_file))
                self.last_graph_state = current_graph.copy()
                
            # Vector B: Sample live node proxy latency RTT overhead
            raw_latency_matrix = self.telemetry.sample_round_trip()
            with open(self.telemetry_file, 'w', encoding='utf-8') as f:
                json.dump(raw_latency_matrix, f, indent=4)
                
            # Notify UI layers via global atomic signal block
            signal_file = self.matrix_file.parent / ".refresh_signal"
            signal_file.write_text(str(asyncio.get_event_loop().time()))
                
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
        logger.info("👋 Broadcast server shut down cleanly.")
