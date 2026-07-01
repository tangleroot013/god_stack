import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[MATRIX-AUDIT]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixAudit")

class WorkspaceComponentAuditor:
    def __init__(self):
        self.critical_modules = [
            "adaptive_concurrency.py", "db_guard.py", "hot_config.py",
            "dual_buffer.py", "sandbox_queue.py", "dead_letter_stream.py",
            "heartbeat_server.py", "vfs_vacuum.py", "central_supervisor.py",
            "tls_obfuscator.py", "telemetry_sync.py", "http2_pool.py",
            "dom_drift_watchdog.py", "node_coordinator.py", "payload_obfuscator.py",
            "latency_monitor.py", "subprocess_watchdog.py", "profile_rotator.py",
            "semantic_stripper.py", "recovery_driver.py", "log_ring.py",
            "selector_matcher.py", "affinity_router.py"
        ]

    def verify_workspace_integrity(self) -> bool:
        print("\n\033[1;32m--- G.O.D. COMPLETE ARCHITECTURAL INTEGRITY AUDIT ---\033[0m")
        logger.info(f"Scanning project workspace path for structural dependencies...")
        missing_count = 0
        
        for file_node in self.critical_modules:
            if os.path.exists(file_node):
                logger.info(f"  Component Checkpoint [ \033[1;32mOK\033[0m ]: {file_node}")
            else:
                logger.error(f"  Component Checkpoint [ \033[1;31mMISSING\033[0m ]: {file_node}")
                missing_count += 1
                
        if missing_count == 0:
            logger.info("\033[1;32mAll core micro-module architecture blocks are fully deployed on disk.\033[0m")
            return True
        else:
            logger.critical(f"Integrity check failed. Total structural deficiencies found: {missing_count}")
            return False

if __name__ == "__main__":
    auditor = WorkspaceComponentAuditor()
    all_clear = auditor.verify_workspace_integrity()
    if not all_clear:
        sys.exit(1)
    print("\n\033[1;32m✔ MODULE 66 INTEGRITY VERIFICATION MATRIX CONVERGED.\033[0m\n")
