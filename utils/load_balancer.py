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
HISTORICAL_METRICS_FILE = PROJECT_ROOT / "vaults" / ".load_balancer_meta.json"

THRESHOLDS = {
    "HI_PRIORITY_SATURATION": 100,
    "HI_PRIORITY_RECOVERY": 30,
    "STANDARD_SATURATION": 1200,
    "STANDARD_RECOVERY": 500,
    "CPU_MAX_THRESHOLD": 85.0,
    "CPU_RECOVERY_THRESHOLD": 65.0
}

ALPHA = 0.3
DEFAULT_DRAIN_RATE = 50.0

class ClusterOrchestrator:
    def __init__(self):
        # Ensure SHM file space is cleanly allocated (4096 bytes page baseline)
        SHM_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not SHM_FILE.exists():
            with open(SHM_FILE, "wb") as f:
                f.write(b"\x00" * 4096)

    def _get_previous_meta(self):
        if HISTORICAL_METRICS_FILE.exists():
            try:
                with open(HISTORICAL_METRICS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"global_action": "NOMINAL", "calculated_drain_rates": {}, "timestamp_updated": time.time() - 2, "_debug_raw_metrics": {}}

    def evaluate_cluster_health(self):
        if not STATE_FILE.exists():
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            prev_meta = self._get_previous_meta()
            previous_action = prev_meta.get("global_action", "NOMINAL")
            prev_drain_rates = prev_meta.get("calculated_drain_rates", {})
            prev_timestamp = prev_meta.get("timestamp_updated", time.time() - 2)
            
            current_time = time.time()
            delta_t = max(0.1, current_time - prev_timestamp)
            
            global_action = "NOMINAL"
            current_drain_rates = {}

            # Evaluate targeted single worker topology baseline
            worker = "Worker-00"
            stats = diagnostics.get(worker, {})
            
            hi_lane = stats.get("priority_lane_depth", 0)
            std_lane = stats.get("standard_lane_depth", 0)
            cpu = stats.get("cpu_util", 0.0)
            current_total_q = stats.get("queue_depth", 0)

            historical_worker_state = prev_meta.get("_debug_raw_metrics", {}).get(worker, {})
            prev_total_q = historical_worker_state.get("queue_depth", current_total_q)
            
            items_cleared = max(0, prev_total_q - current_total_q)
            instant_drain_rate = items_cleared / delta_t
            
            worker_prev_ema = prev_drain_rates.get(worker, DEFAULT_DRAIN_RATE)
            smoothed_drain_rate = (ALPHA * instant_drain_rate) + ((1 - ALPHA) * worker_prev_ema)
            
            if smoothed_drain_rate < 1.0:
                smoothed_drain_rate = 5.0
            
            current_drain_rates[worker] = round(smoothed_drain_rate, 2)

            # State Machine Check
            if previous_action == "THROTTLE_INGESTION":
                if hi_lane > THRESHOLDS["HI_PRIORITY_RECOVERY"] or std_lane > THRESHOLDS["STANDARD_RECOVERY"] or cpu > THRESHOLDS["CPU_RECOVERY_THRESHOLD"]:
                    global_action = "THROTTLE_INGESTION"
            elif previous_action == "SHED_LOAD":
                if hi_lane > THRESHOLDS["HI_PRIORITY_SATURATION"]:
                    global_action = "THROTTLE_INGESTION"
                elif std_lane > THRESHOLDS["STANDARD_RECOVERY"] or cpu > THRESHOLDS["CPU_RECOVERY_THRESHOLD"]:
                    global_action = "SHED_LOAD"
            else:
                if hi_lane >= THRESHOLDS["HI_PRIORITY_SATURATION"]:
                    global_action = "THROTTLE_INGESTION"
                elif std_lane >= THRESHOLDS["STANDARD_SATURATION"] or cpu >= THRESHOLDS["CPU_MAX_THRESHOLD"]:
                    global_action = "SHED_LOAD"

            if global_action != previous_action:
                if global_action == "THROTTLE_INGESTION":
                    logger.error("🛑 CRITICAL LOCK DOWN: High-priority bounds breached. Complete ingestion halt.")
                elif global_action == "SHED_LOAD":
                    logger.warning("⚠️ SHED_LOAD ACTIVE: Standard lane saturated. Dropping edge ingestion lanes.")
                elif global_action == "NOMINAL":
                    logger.info("🟢 NOMINAL RESTORED: All lanes reporting below clearing parameters.")

            # PERSISTENCE OPTIMIZATION: Write payload to shared memory mmap handle
            action_bytes = global_action.encode('utf-8').ljust(12, b'\x00')
            packed_shm_payload = struct.pack("<12sddI", action_bytes, smoothed_drain_rate, float(current_time), std_lane)
            
            with open(SHM_FILE, "r+b") as f:
                with mmap.mmap(f.fileno(), 0) as mm:
                    mm[0:len(packed_shm_payload)] = packed_shm_payload
                    mm.flush()

            # Maintain historical tracking log outside the hot path
            with open(HISTORICAL_METRICS_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "global_action": global_action,
                    "calculated_drain_rates": current_drain_rates,
                    "timestamp_updated": current_time,
                    "_debug_raw_metrics": diagnostics
                }, f)

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
