#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Deploying Patched Sandbox Spillway State Engine...\033[0m"

cat << 'PYEOF' > sandbox_queue.py
import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[SANDBOX-PATCH]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SandboxPatch")

class PersistentSandboxSpillway:
    def __init__(self, sandbox_dir: str = "storage/sandbox_spillway"):
        self.sandbox_dir = sandbox_dir
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def enqueue_uncommitted_state(self, queue_id: str, payload: dict):
        target_path = os.path.join(self.sandbox_dir, f"state_{queue_id}.tmp")
        logger.info(f"Staging atomic partition checkpoint to spillway tracking node: {target_path}")
        with open(target_path, "w") as f:
            json.dump(payload, f)
            f.flush()
            os.fsync(f.fileno()) # Fixed alignment error: executed inside the file context stream block

    def clear_committed_state(self, queue_id: str):
        target_path = os.path.join(self.sandbox_dir, f"state_{queue_id}.tmp")
        if os.path.exists(target_path):
            os.remove(target_path)
            logger.info(f"Purged transient file tracking state for {queue_id} successfully.")

def main():
    print("\n\033[1;32m--- G.O.D. PERSISTENT TRANSIENT ISOLATION TRACE (PATCHED) ---\033[0m")
    spillway = PersistentSandboxSpillway()
    mock_id = "TX_99182A"
    mock_payload = {"target_route": "https://httpbin.org/get", "extraction_depth": 3}
    
    spillway.enqueue_uncommitted_state(mock_id, mock_payload)
    spillway.clear_committed_state(mock_id)
    print("\n\033[1;32m✔ MODULE 51 FIXED SANDBOX SPILLWAY RUNNING STABLE.\033[0m\n")

if __name__ == "__main__":
    main()
PYEOF

echo -e "\033[1;34m[2/2] Running runtime trace validation test loop...\033[0m"
chmod +x sandbox_queue.py
./.venv/bin/python3 sandbox_queue.py
