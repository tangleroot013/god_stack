import sys
import os
import asyncio
import logging
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver

# Dynamically extract absolute project root framework path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from utils.search_ledger import SearchLedger

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BroadcastDaemon")

class LiveWatcher:
    def __init__(self):
        # Anchor explicitly using absolute paths
        self.watch_dir = ROOT_DIR / "vaults" / "intelligence_graph"
        self.matrix_file = ROOT_DIR / "vaults" / "matrix_map.json"
        self.ledger = SearchLedger(vault_path=str(self.watch_dir))
        self.last_state = None

    async def watch_loop(self):
        logger.info(f"📡 File system watcher activated. Monitoring: {self.watch_dir}")
        while True:
            current_graph = self.ledger.build_ledger()
            
            if self.last_state is None or current_graph != self.last_state:
                logger.info("🔄 Topology change or initialization detected! Syncing matrix map...")
                self.ledger.export_matrix(output_file=str(self.matrix_file))
                self.last_state = current_graph.copy()
                
                signal_file = self.matrix_file.parent / ".refresh_signal"
                signal_file.write_text(str(asyncio.get_event_loop().time()))
                
            await asyncio.sleep(2)

def run_http_server():
    # Keep directory reference safely locked to the vaults folder
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
