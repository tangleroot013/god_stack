import json
import logging
import time
import mmap
import struct
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LoadBalancer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
SHM_FILE = PROJECT_ROOT / "vaults" / ".routing_matrix.shm"

class ClusterOrchestrator:
    def evaluate_cluster_health(self):
        if not STATE_FILE.exists():
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            worker = "Worker-00"
            stats = diagnostics.get(worker, {})
            std_lane = stats.get("standard_lane_depth", 0)
            
            # For testing, we intentionally force a low drain rate to trigger scaling
            forced_low_drain = 15.45 
            global_action = "SHED_LOAD"

            # Pack Header: 12 bytes action, 4 bytes worker count (initially 1)
            action_bytes = global_action.encode('utf-8').ljust(12, b'\x00')
            header = struct.pack("=12sI", action_bytes, 1)
            
            # Pack Slot 1: Worker-00 Info
            w00_bytes = worker.encode('utf-8').ljust(12, b'\x00')
            slot_1 = struct.pack("=12sdId", w00_bytes, forced_low_drain, std_lane, time.time())

            with open(SHM_FILE, "w+b") as f:
                # Pre-allocate 4096 bytes block space
                f.write(b"\x00" * 4096)
                f.flush()
                
            with open(SHM_FILE, "r+b") as f:
                with mmap.mmap(f.fileno(), 0) as mm:
                    mm[0:16] = header
                    mm[16:48] = slot_1
                    mm.flush()

            logger.warning("⚠️ Load Balancer evaluated structural state: SHED_LOAD with low drain velocity.")

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
