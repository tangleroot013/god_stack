#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Organizing Infrastructure Janitor Subsystem...\033[0m"

cat << 'PYEOF' > env_janitor.py
import os
import logging
from glob import glob

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;36m[JANITOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EnvJanitor")

class SystemWorkspaceJanitor:
    def __init__(self, workspace_dir: str = "."):
        self.workspace = workspace_dir

    def purge_runtime_debris(self):
        print("\n\033[1;32m--- G.O.D. WORKSPACE DEBRIS SANITIZATION PURGE ---\033[0m")
        
        # Gather debris patterns
        patterns = ["*.pyc", "__pycache__", ".pytest_cache", "patch_and_run_unification.sh"]
        purged_count = 0
        
        for pattern in patterns:
            targets = glob(os.path.join(self.workspace, "**", pattern), recursive=True) + glob(os.path.join(self.workspace, pattern))
            for target in targets:
                try:
                    if os.path.isdir(target):
                        os.rmdir(target)
                    else:
                        os.remove(target)
                    logger.info(f"Safely purged architecture debris item: {os.path.basename(target)}")
                    purged_count += 1
                except Exception:
                    pass

        logger.info(f"Purge sequence finalized. Cleaned up ({purged_count}) temporary workspace fragments.")

if __name__ == "__main__":
    janitor = SystemWorkspaceJanitor()
    janitor.purge_runtime_debris()
    print("\n\033[1;32m✔ MODULE 35 ECO-JANITOR DEPLOYMENT MATRIX CLEANED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Running runtime workspace grooming pass...\033[0m"
chmod +x env_janitor.py
./.venv/bin/python3 env_janitor.py
