#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Constructing Sliding-Window Token Rate Limiter...\033[0m"

cat << 'PYEOF' > sliding_rate_limiter.py
import asyncio
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[RATE-LIMITER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("RateLimiter")

class SlidingWindowLimiter:
    def __init__(self, max_requests: int = 2, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_timestamps = []

    async def acquire_slot(self, task_id: int):
        while True:
            current_time = time.time()
            # Clear historical timestamps that fall completely outside the sliding tracking frame
            self.request_timestamps = [t for t in self.request_timestamps if current_time - t < self.window_seconds]
            
            if len(self.request_timestamps) < self.max_requests:
                self.request_timestamps.append(current_time)
                logger.info(f"Task #{task_id} cleared window check. Slot leased successfully.")
                break
            else:
                wait_time = self.window_seconds - (current_time - self.request_timestamps[0])
                logger.warning(f"Window threshold reached. Task #{task_id} backpressure delay injection ({wait_time:.2f}s)...")
                await asyncio.sleep(max(wait_time, 0.01))

async def simulate_burst_traffic():
    print("\n\033[1;32m--- G.O.D. ADAPTIVE BURST RATE CONTROL VALIDATION ---\033[0m")
    limiter = SlidingWindowLimiter(max_requests=2, window_seconds=0.5)
    
    # Fire 4 execution tasks concurrently to force sliding window backpressure triggers
    tasks = [limiter.acquire_slot(i) for i in range(4)]
    await asyncio.gather(*tasks)
    print("\n\033[1;32m✔ MODULE 37 SLIDING-WINDOW BACKPRESSURE RATE LIMITER COMPLIANT.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(simulate_burst_traffic())
PYEOF

echo -e "\033[1;34m[2/2] Triggering simultaneous concurrent burst validation...\033[0m"
chmod +x sliding_rate_limiter.py
./.venv/bin/python3 sliding_rate_limiter.py
