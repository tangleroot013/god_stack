import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("VaultSync")

class VaultSyncHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/vault/sync":
            content_length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(content_length)
            
            try:
                data = json.loads(payload.decode('utf-8'))
                log.info(f"💾 Ingested pipeline transaction packet for target: {data.get('url')}")
                
                # Respond with a successful transactional handshake
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "SUCCESS", "vaulted": True}).encode('utf-8'))
            except Exception as e:
                log.error(f"Failed to parse payload: {e}")
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default server access logs to keep terminal streams clean
        return

def run_server():
    server_address = ('127.0.0.1', 8890)
    httpd = HTTPServer(server_address, VaultSyncHandler)
    log.info("📡 Vault Sync API Receiver Online. Listening on http://127.0.0.1:8890")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("Vault Sync API Receiver shutting down cleanly.")

if __name__ == "__main__":
    run_server()
