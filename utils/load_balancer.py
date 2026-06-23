import json
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LoadBalancer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
ROUTING_MAP_FILE = PROJECT_ROOT / "vaults" / "optimized_routing.json"

THRESHOLDS = {
    "HI_PRIORITY_SATURATION": 100,
    "HI_PRIORITY_RECOVERY": 30,
    "STANDARD_SATURATION": 1200,
    "STANDARD_RECOVERY": 500,
    "CPU_MAX_THRESHOLD": 85.0,
    "CPU_RECOVERY_THRESHOLD": 65.0
}

# EMA Configuration
ALPHA = 0.3  # Weight of new data vs history
DEFAULT_DRAIN_RATE = 50.0

class ClusterOrchestrator:
    def _get_previous_routing(self):
        if ROUTING_MAP_FILE.exists():
            try:
                with open(ROUTING_MAP_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def evaluate_cluster_health(self):
        if not STATE_FILE.exists():
            logger.warning("Awaiting cluster state payload generation...")
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            prev_routing = self._get_previous_routing()
            previous_action = prev_routing.get("global_action", "NOMINAL")
            prev_drain_rates = prev_routing.get("calculated_drain_rates", {})
            prev_timestamp = prev_routing.get("timestamp_updated", time.time() - 2)
            
            current_time = time.time()
            delta_t = max(0.1, current_time - prev_timestamp)
            
            global_action = "NOMINAL"
            current_drain_rates = {}

            for worker, stats in diagnostics.items():
                hi_lane = stats.get("priority_lane_depth", 0)
                std_lane = stats.get("standard_lane_depth", 0)
                cpu = stats.get("cpu_util", 0.0)
                current_total_q = stats.get("queue_depth", 0)

                # Fetch historical snapshots from the routing file
                # To calculate real drain, we check total queue delta
                # (Alternatively, you can track per-lane history if desired)
                # For safety, we fall back to a standard queue depth profile if missing
                historical_worker_state = prev_routing.get("_debug_raw_metrics", {}).get(worker, {})
                prev_total_q = historical_worker_state.get("queue_depth", current_total_q)
                
                # Calculate processing velocity: delta_Q dropped / delta_t
                # Maxed at 0 to ensure we only look at items *cleared*
                items_cleared = max(0, prev_total_q - current_total_q)
                instant_drain_rate = items_cleared / delta_t
                
                # Smooth the rate using EMA
                worker_prev_ema = prev_drain_rates.get(worker, DEFAULT_DRAIN_RATE)
                smoothed_drain_rate = (ALPHA * instant_drain_rate) + ((1 - ALPHA) * worker_prev_ema)
                
                # Protect against division-by-zero or stalled-worker anomalies
                if smoothed_drain_rate < 1.0:
                    smoothed_drain_rate = 5.0
                
                current_drain_rates[worker] = round(smoothed_drain_rate, 2)

                # State Machine Evaluation Hysteresis
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

            # Record state along with historical telemetry cache for next delta delta evaluations
            with open(ROUTING_MAP_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "cluster_healthy": global_action == "NOMINAL",
                    "global_action": global_action,
                    "calculated_drain_rates": current_drain_rates,
                    "timestamp_updated": current_time,
                    "_debug_raw_metrics": diagnostics  # Persisted snapshot to calculate next frame's delta
                }, f, indent=4)

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
