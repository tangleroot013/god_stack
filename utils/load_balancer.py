import json
import logging
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LoadBalancer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
ROUTING_MAP_FILE = PROJECT_ROOT / "vaults" / "optimized_routing.json"

# Operational Lane Threshold Configurations
THRESHOLDS = {
    "HI_PRIORITY_SATURATION": 100,     # Max tolerated critical lane depth
    "HI_PRIORITY_RECOVERY": 30,        # Safe clearing target for critical lane
    "STANDARD_SATURATION": 1200,       # Max tolerated background lane depth
    "STANDARD_RECOVERY": 500,          # Safe clearing target for background lane
    "CPU_MAX_THRESHOLD": 85.0,         # Maximum sustainable CPU utilization
    "CPU_RECOVERY_THRESHOLD": 65.0     # Target cooled down CPU percentage
}

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
        """Processes lane-aware matrices to govern graceful degradation states."""
        if not STATE_FILE.exists():
            logger.warning("Awaiting cluster state payload generation...")
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            prev_routing = self._get_previous_routing()
            previous_action = prev_routing.get("global_action", "NOMINAL")
            
            global_action = "NOMINAL"
            total_workers = len(diagnostics)
            
            # Aggregate lane states across the worker cluster
            for worker, stats in diagnostics.items():
                hi_lane = stats.get("priority_lane_depth", 0)
                std_lane = stats.get("standard_lane_depth", 0)
                cpu = stats.get("cpu_util", 0.0)

                # Hysteresis Execution Logic
                if previous_action == "THROTTLE_INGESTION":
                    # Lock down recovery loop: Require cooldown past recovery levels
                    if hi_lane > THRESHOLDS["HI_PRIORITY_RECOVERY"] or std_lane > THRESHOLDS["STANDARD_RECOVERY"] or cpu > THRESHOLDS["CPU_RECOVERY_THRESHOLD"]:
                        global_action = "THROTTLE_INGESTION"
                elif previous_action == "SHED_LOAD":
                    # Shedding recovery loop
                    if hi_lane > THRESHOLDS["HI_PRIORITY_SATURATION"]:
                        global_action = "THROTTLE_INGESTION"
                    elif std_lane > THRESHOLDS["STANDARD_RECOVERY"] or cpu > THRESHOLDS["CPU_RECOVERY_THRESHOLD"]:
                        global_action = "SHED_LOAD"
                else:
                    # Nominal assessment loop
                    if hi_lane >= THRESHOLDS["HI_PRIORITY_SATURATION"]:
                        global_action = "THROTTLE_INGESTION"
                    elif std_lane >= THRESHOLDS["STANDARD_SATURATION"] or cpu >= THRESHOLDS["CPU_MAX_THRESHOLD"]:
                        global_action = "SHED_LOAD"

            # Log precise structural state modifications
            if global_action != previous_action:
                if global_action == "THROTTLE_INGESTION":
                    logger.error(f"🛑 CRITICAL LOCK DOWN: High-priority bounds breached. Complete ingestion halt.")
                elif global_action == "SHED_LOAD":
                    logger.warning(f"⚠️ SHED_LOAD ACTIVE: Standard lane saturated. Bouncing standard traffic, keeping priority line open.")
                elif global_action == "NOMINAL":
                    logger.info(f"🟢 NOMINAL RESTORED: All lanes reporting below clearing parameters.")

            with open(ROUTING_MAP_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "cluster_healthy": global_action == "NOMINAL",
                    "global_action": global_action,
                    "calculated_drain_rates": prev_routing.get("calculated_drain_rates", {"Worker-00": 50.0}),
                    "timestamp_updated": time.time()
                }, f, indent=4)

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
