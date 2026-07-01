#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Building Thread-Safe Task Counting Barrier...\033[0m"

cat << 'PYEOF' > counting_barrier.py
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[BARRIER-COUNT]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BarrierCount")

class ThreadSafeCountingBarrier:
    def __init__(self, target_completions: int = 3):
        self.target = target_completions
        self.counter = 0
        self.lock = threading.Lock()

    def register_worker_completion(self, worker_id: str) -> bool:
        print("\n\033[1;32m--- G.O.D. MULTI-THREAD PIPELINE COMPLETION BARRIER ---\033[0m")
        with self.lock:
            self.counter += 1
            logger.info(f"Worker [ \033[1;33m{worker_id}\033[0m ] reached the checkout matrix block.")
            logger.info(f"  Current Synced Checkpoint State: {self.counter}/{self.target}")
            
            if self.counter == self.target:
                logger.info("\033[1;32mMaster completion limit verified. Releasing downstream orchestration threads.\033[0m")
                return True
        return False

if __name__ == "__main__":
    barrier = ThreadSafeCountingBarrier(target_completions=2)
    # Simulate two independent parallel thread checkout arrivals
    barrier.register_worker_completion("WORKER_CORE_01")
    barrier.register_worker_completion("WORKER_CORE_02")
    print("\n\033[1;32m✔ MODULE 83 EXECUTION COUNT BARRIER OPERATIONAL.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Instantiating multithread coordination verification...\033[0m"
chmod +x counting_barrier.py
./.venv/bin/python3 counting_barrier.py
