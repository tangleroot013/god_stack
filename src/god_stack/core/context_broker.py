import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[CONTEXT-BROKER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ContextBroker")

class InterModuleGlobalContextBroker:
    def __init__(self):
        self._shared_state = {}
        self._lock = threading.Lock()

    def publish_shared_parameter(self, key: str, value: any):
        print("\n\033[1;32m--- G.O.D. VOLATILE MEMORY CONTEXT EXCHANGER ---\033[0m")
        with self._lock:
            self._shared_state[key] = value
            logger.info(f"Inter-process variable published: [ \033[1;33m{key}\033[0m ]")
            logger.info(f"  Context Register Map Updated.")

    def fetch_shared_parameter(self, key: str, default_fallback: any = None) -> any:
        with self._lock:
            return self._shared_state.get(key, default_fallback)

if __name__ == "__main__":
    broker = InterModuleGlobalContextBroker()
    broker.publish_shared_parameter("CLUSTER_STATUS_CODE", "READY_TO_STREAM")
    print("\n\033[1;32m✔ MODULE 103 CROSS-THREAD DATA BROKERS ACTIVE.\033[0m\n")
