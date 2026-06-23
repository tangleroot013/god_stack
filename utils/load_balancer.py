import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("LoadBalancer")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"
ROUTING_MAP_FILE = PROJECT_ROOT / "vaults" / "optimized_routing.json"

class ClusterOrchestrator:
    def __init__(self, queue_threshold=1000, cpu_threshold=80.0):
        self.queue_threshold = queue_threshold
        self.cpu_threshold = cpu_threshold

    def evaluate_cluster_health(self):
        """Analyzes cluster_state.json and generates adaptive edge backpressure rules."""
        if not STATE_FILE.exists():
            logger.warning("Awaiting cluster state payload generation...")
            return

        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)

            diagnostics = state.get("worker_diagnostics", {})
            
            routing_overrides = {}
            unhealthy_nodes = []
            healthy_alternatives = []

            for worker, stats in diagnostics.items():
                q_depth = stats.get("queue_depth", 0)
                cpu = stats.get("cpu_util", 0.0)

                if q_depth > self.queue_threshold or cpu > self.cpu_threshold:
                    logger.warning(f"🚨 CRITICAL OVERLOAD: {worker} [Queue: {q_depth}, CPU: {cpu}%]")
                    unhealthy_nodes.append(worker)
                else:
                    healthy_alternatives.append(worker)

            # Determine global pressure state
            global_action = "NOMINAL"
            if unhealthy_nodes:
                if not healthy_alternatives:
                    # COMPLETE CLUSTER SATURATION PROTOCOL
                    logger.error("🛑 SYSTEM SATURATED: Zero fallback routes available. Activating Edge Backpressure.")
                    global_action = "THROTTLE_INGESTION"
                    for node in unhealthy_nodes:
                        routing_overrides[node] = {
                            "status": "SATURATED",
                            "action": "THROTTLE_INGESTION"
                        }
                else:
                    # Standard load shedding routing
                    global_action = "SHED_LOAD"
                    fallback_target = healthy_alternatives[0]
                    for node in unhealthy_nodes:
                        routing_overrides[node] = {
                            "status": "SHEDDING_LOAD",
                            "divert_target": fallback_target,
                            "action": "HALT_NEW_INGESTION"
                        }
            else:
                logger.info("🟢 Cluster optimization profiles nominal.")

            # Drop instructions for the HTTP Gateway
            with open(ROUTING_MAP_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "cluster_healthy": len(unhealthy_nodes) == 0,
                    "global_action": global_action,
                    "overrides": routing_overrides
                }, f, indent=4)

        except Exception as e:
            logger.error(f"Optimization matrix execution failure: {e}")

if __name__ == "__main__":
    orchestrator = ClusterOrchestrator()
    orchestrator.evaluate_cluster_health()
