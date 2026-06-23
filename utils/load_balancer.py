import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LoadBalancer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
ROUTING_MAP_FILE = PROJECT_ROOT / "vaults" / "optimized_routing.json"

class ClusterOrchestrator:
    def __init__(self, high_queue=1000, high_cpu=80.0, low_queue=600, low_cpu=60.0):
        self.high_queue = high_queue
        self.high_cpu = high_cpu
        self.low_queue = low_queue
        self.low_cpu = low_cpu

    def _get_previous_action(self):
        if ROUTING_MAP_FILE.exists():
            try:
                with open(ROUTING_MAP_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f).get("global_action", "NOMINAL")
            except:
                pass
        return "NOMINAL"

    def evaluate_cluster_health(self):
        """Calculates adaptive state changes using a strict hysteresis buffer."""
        if not STATE_FILE.exists():
            logger.warning("Awaiting cluster state payload generation...")
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            previous_action = self._get_previous_action()
            
            routing_overrides = {}
            unhealthy_count = 0
            total_workers = len(diagnostics)
            recovering_nodes = []

            for worker, stats in diagnostics.items():
                q_depth = stats.get("queue_depth", 0)
                cpu = stats.get("cpu_util", 0.0)

                # Determine health using memory of previous state (hysteresis)
                if previous_action == "THROTTLE_INGESTION":
                    # We are locked down. Node must fall below recovery limits to clear.
                    if q_depth > self.low_queue or cpu > self.low_cpu:
                        unhealthy_count += 1
                    else:
                        recovering_nodes.append(worker)
                else:
                    # System is nominal. Node triggers alert at high threshold.
                    if q_depth > self.high_queue or cpu > self.high_cpu:
                        unhealthy_count += 1

            # Determine global pressure state transition rules
            global_action = "NOMINAL"
            if unhealthy_count > 0:
                if unhealthy_count == total_workers or total_workers == 1:
                    global_action = "THROTTLE_INGESTION"
                    logger.error(f"🛑 LOCK DOWN ACTIVE: Cluster saturated. [{unhealthy_count}/{total_workers} workers failed]")
                else:
                    global_action = "SHED_LOAD"
            elif previous_action == "THROTTLE_INGESTION" and recovering_nodes:
                # Part of the cluster dropped below recovery marks, but let's confirm full clearance
                global_action = "THROTTLE_INGESTION"
                logger.warning("⏳ COOLING DOWN: Workers draining queues below recovery limits...")

            if global_action == "NOMINAL" and previous_action == "THROTTLE_INGESTION":
                logger.info("🟢 RECOVERY COMPLETE: Cluster states safely normalized. Re-opening edge ingestion gates.")

            # Write instructions to state management file
            with open(ROUTING_MAP_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "cluster_healthy": global_action == "NOMINAL",
                    "global_action": global_action,
                    "metrics_summary": {
                        "active_alerts": unhealthy_count,
                        "recovering_pool": recovering_nodes
                    }
                }, f, indent=4)

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
