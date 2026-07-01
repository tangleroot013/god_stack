#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating Stateful Jittered Backoff Machine...\033[0m"

cat << 'PYEOF' > jittered_retry.py
import asyncio
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;33m[RETRY-ENGINE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("JitteredRetry")

class ResilientRetryCircuit:
    def __init__(self, max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 4.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    async def execute_with_jitter(self, task_fn, *args, **kwargs):
        print("\n\033[1;32m--- G.O.D. RANDOMIZED RETRY MATRIX WORKFLOW ---\033[0m")
        attempt = 0
        
        while attempt <= self.max_retries:
            try:
                return await task_fn(attempt, *args, **kwargs)
            except Exception as e:
                attempt += 1
                if attempt > self.max_retries:
                    logger.critical(f"All {self.max_retries} retry vectors exhausted. Permanent failure state.")
                    raise e
                
                # Apply Full Jitter calculation: Sleep = random(0, min(max_delay, base_delay * 2 ^ attempt))
                calculated_backoff = min(self.max_delay, self.base_delay * (2 ** attempt))
                jittered_sleep = random.uniform(0, calculated_backoff)
                
                logger.warning(
                    f"Attempt #{attempt} hit barrier structural stall: {e}. "
                    f"Backing off for {jittered_sleep:.3f}s (Max ceiling: {calculated_backoff:.2f}s)..."
                )
                await asyncio.sleep(jittered_sleep)

# Simulated fragile endpoint worker
async def mock_network_fetch(attempt):
    if attempt < 2:
        raise ConnectionResetError("Remote server closed control socket connection abruptly.")
    logger.info("\033[1;32mSuccess!\033[0m Target handoff completed cleanly on retry phase.")
    return {"status": "SUCCESS_DATA"}

async def main():
    circuit = ResilientRetryCircuit()
    await circuit.execute_with_jitter(mock_network_fetch)
    print("\n\033[1;32m✔ MODULE 39 STATEFUL JITTER BACKOFF COMPLIANT.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF

echo -e "\033[1;34m[2/2] Running runtime trace validation test loop...\033[0m"
chmod +x jittered_retry.py
./.venv/bin/python3 jittered_retry.py
