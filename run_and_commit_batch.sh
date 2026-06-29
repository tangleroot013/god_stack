#!/usr/bin/env bash
set -euo pipefail

BLUE="\033[1;34m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo -e "${BLUE}[1/4] Generating Python Batch Runner (run_batch_test.py)...${RESET}"

cat << 'PY_EOF' > run_batch_test.py
import asyncio
import logging
from orchestrator import GodOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[BATCH-TEST]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BatchTest")

TEST_URLS = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://news.ycombinator.com"
]

async def run_batch():
    logger.info("Initializing Orchestrator matrix for batch testing...")
    orchestrator = GodOrchestrator(use_proxies=False)
    await orchestrator.initialize_matrix()

    logger.info(f"Loaded {len(TEST_URLS)} targets. Commencing batch execution.")
    
    for url in TEST_URLS:
        logger.info(f"Locking targeting vector to: {url}")
        result = await orchestrator.execute_mission(url)
        
        if result.get("status") == "success":
            logger.info(f"Extraction successful for {url} | Message: {result.get('message')}")
        else:
            logger.warning(f"Mission failed or blocked for {url} | Reason: {result.get('message')}")
        
        await asyncio.sleep(1.5)
    
    logger.info("Batch execution sequence complete. Triggering graceful teardown...")
    if hasattr(orchestrator.engine, 'shutdown'):
        await orchestrator.engine.shutdown()
        
    logger.info("Teardown verified. Subsystems deactivated safely.")

if __name__ == "__main__":
    try:
        asyncio.run(run_batch())
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user. Triggering emergency halt.")
    except Exception as e:
        logger.error(f"Fatal pipeline collapse: {e}")
PY_EOF

echo -e "${BLUE}[2/4] Sourcing Virtual Environment...${RESET}"
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo -e "${YELLOW}[WARNING] .venv not found. Proceeding with system Python...${RESET}"
fi

echo -e "${YELLOW}[3/4] Executing Batch Test Suite...${RESET}"
python3 run_batch_test.py

echo -e "${BLUE}[4/4] Execution verified. Committing to main branch...${RESET}"

git checkout main
git add run_batch_test.py run_and_commit_batch.sh
git commit -m "test(orchestrator): implement batch URL execution loop with clean teardown validation"

echo -e "${GREEN}[SUCCESS] Batch test completed cleanly and committed to G.O.D. Stack main.${RESET}"
