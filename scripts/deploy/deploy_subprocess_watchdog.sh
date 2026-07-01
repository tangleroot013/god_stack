#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Deploying Subprocess Worker Matrix Supervisor...\033[0m"

cat << 'PYEOF' > subprocess_watchdog.py
import subprocess
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[PROC-WATCHDOG]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SubprocessWatchdog")

class ClusterProcessSupervisor:
    def __init__(self):
        self.active_monitors = {}

    def run_and_register_worker(self, module_alias: str, command_list: list):
        print("\n\033[1;32m--- G.O.D. SUBPROCESS LIFECYCLE WATCHDOG MATRIX ---\033[0m")
        logger.info(f"Spawning tracking target allocation context for: {module_alias}")
        
        # Spawn a non-blocking process frame structure
        proc = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.active_monitors[module_alias] = proc
        logger.info(f"  Worker registered under system process tracking tree. PID assigned: #{proc.pid}")

    def audit_process_vitality(self) -> bool:
        healthy = True
        for alias, proc in list(self.active_monitors.items()):
            poll_status = proc.poll()
            if poll_status is None:
                logger.info(f"Subprocess context [ \033[1;32m{alias}\033[0m ] is executing normally (PID #{proc.pid}).")
            else:
                logger.error(f"Subprocess context [ \033[1;31m{alias}\033[0m ] dropped execution thread unexpectedly with Exit Code: {poll_status}")
                healthy = False
                # Re-clean and purge file tracking keys
                proc.kill()
                del self.active_monitors[alias]
        return healthy

if __name__ == "__main__":
    supervisor = ClusterProcessSupervisor()
    # Spin up a fast-exiting clean system call node to demonstrate state change intercept logic
    supervisor.run_and_register_worker("MOCK_CORE_WORKER", [sys.executable, "-c", "import time; time.sleep(0.01)"])
    
    import time
    time.sleep(0.05) # Allow target call context window space to terminate execution
    supervisor.audit_process_vitality()
    print("\n\033[1;32m✔ MODULE 59 SYSTEM EXECUTIVE CRASH SUPERVISOR DEPLOYED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Running sub-layer isolation execution tests...\033[0m"
chmod +x subprocess_watchdog.py
./.venv/bin/python3 subprocess_watchdog.py
