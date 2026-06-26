# =============================================================================
# G.O.D. STACK INTEGRATION HUB (run_stack_pipeline.py)
# Architecture: Core Pipeline Automation, Testing & Sweeper Bridge
# =============================================================================

import asyncio
import subprocess
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[CORE-HUB]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CoreHub")

def execute_step(label: str, command: list) -> bool:
    """Runs a sub-process step cleanly and captures exit indicators."""
    print(f"\n\033[1;35m--- STEP: {label} ---\033[0m")
    try:
        result = subprocess.run(
            command,
            check=True,
            text=True
        )
        logger.info(f"\033[1;32m[PASSED]\033[0m Step completed successfully: {label}")
        return True
    except subprocess.CalledProcessError as err:
        logger.error(f"\033[1;31m[FAILED]\033[0m Critical failure in step {label}. Code: {err.returncode}")
        return False

async def main():
    print("\n\033[1;33m==================================================\033[0m")
    print("\033[1;33m      LAUNCHING INTEGRATED G.O.D. PIPELINE        \033[0m")
    print("\033[1;33m==================================================\033[0m")

    # Step 1: Enforce code correctness via regression testing suite
    if not execute_step("Regression Test Sweep", [".venv/bin/python3", "-m", "unittest", "tests/test_core_utilities.py", "-v"]):
        print("\033[1;31mAborting pipeline: Core validation tests failed.\033[0m")
        sys.exit(1)

    # Step 2: Fire legacy fallback batch runner matrix
    if not execute_step("Legacy Grid Dispatch", [".venv/bin/python3", "batch_runner.py"]):
        print("\033[1;31mAborting pipeline: Legacy batch run encountered faults.\033[0m")
        sys.exit(1)

    print("\n\033[1;32m==================================================\033[0m")
    print("\033[1;32m   🎉 ALL CORE STACK MATRICES EXECUTION SECURED   \033[0m")
    print("\033[1;32m==================================================\033[0m")

if __name__ == "__main__":
    asyncio.run(main())
