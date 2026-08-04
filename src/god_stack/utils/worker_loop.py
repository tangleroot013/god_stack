import time
import json
import http.client
from utils.scraper_engine import GodScraperEngine
from utils.dom_parser import GodDOMParser

class GodWorkerNode:
    def __init__(self, gateway_host="localhost", gateway_port=8090):
        self.gateway_host = gateway_host
        self.gateway_port = gateway_port
        self.engine = GodScraperEngine()
        self.running = True

    def poll_gateway_job(self):
        try:
            conn = http.client.HTTPConnection(self.gateway_host, self.gateway_port, timeout=5)
            conn.request("GET", "/next_job")
            res = conn.getresponse()
            
            if res.status == 200:
                data = res.read().decode('utf-8')
                return json.loads(data)
            return None
        except Exception:
            return None

    def execute_loop(self):
        print("🚀 Worker lane context loaded. Interrogating gateway stream with DOM Parsing active...")
        while self.running:
            job = self.poll_gateway_job()
            
            if not job:
                time.sleep(1.0)
                continue
                
            job_id = job.get("job_id")
            target = job.get("sanitized_target")
            print(f"📥 Assigned: [Job {job_id}] -> Target: {target}")
            
            payload_metadata = self.engine.fetch_target(target)
            
            # --- PIPELINE INTERCEPT: Clean raw DOM string before serialization ---
            if payload_metadata["status"] == "SUCCESS":
                raw_html = payload_metadata["raw_data"]
                payload_metadata["raw_data"] = GodDOMParser.extract_clean_text(raw_html)
            
            self.engine.serialize_to_vault(job_id, target, payload_metadata)
            print(f"💾 Flushed parsed result status: {payload_metadata['status']} for [Job {job_id}]")
            
            time.sleep(0.5)

if __name__ == "__main__":
    worker = GodWorkerNode()
    try:
        worker.execute_loop()
    except KeyboardInterrupt:
        print("\n🛑 Worker lane detached cleanly via user interrupt request.")
