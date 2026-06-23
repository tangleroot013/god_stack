import asyncio
import json
import logging
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
import socketserver
from utils.search_ledger import SearchLedger

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BroadcastDaemon")

class LiveWatcher:
    def __init__(self, watch_dir: str = "vaults/intelligence_graph", matrix_file: str = "vaults/matrix_map.json"):
        self.watch_dir = Path(watch_dir)
        self.matrix_file = Path(matrix_file)
        self.ledger = SearchLedger(vault_path=watch_dir)
        self.last_state = {}

    async def watch_loop(self):
        logger.info("📡 File system watcher activated. Monitoring vault modifications...")
        while True:
            # Re-compile ledger dynamically
            current_graph = self.ledger.build_ledger()
            
            # If the topology changed, export and log it
            if current_graph != self.last_state:
                logger.info("🔄 Topology change detected! Re-mapping matrix ledger...")
                self.ledger.export_matrix(output_file=str(self.matrix_file))
                self.last_state = current_graph.copy()
                
                # Write a signaling file for the client polling layer to catch
                signal_file = self.matrix_file.parent / ".refresh_signal"
                signal_file.write_text(str(asyncio.get_event_loop().time()))
                
            await asyncio.sleep(2)  # Non-blocking poll interval

def run_http_server():
    # Serves the vaults directory on 8090
    import os
    os.chdir("vaults")
    handler = SimpleHTTPRequestHandler
    # Allow loose socket re-binding
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8090), handler) as httpd:
        logger.info("🖥️ Retro Web UI server running at http://localhost:8090")
        httpd.serve_forever()

if __name__ == "__main__":
    import threading
    
    # Run HTTP assets server in a background worker thread
    srv_thread = threading.Thread(target=run_http_server, daemon=True)
    srv_thread.start()
    
    # Launch async tracking scheduler
    watcher = LiveWatcher()
    asyncio.run(watcher.watch_loop())
