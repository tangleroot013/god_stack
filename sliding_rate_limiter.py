# =============================================================================
# G.O.D. SLIDING RATE LIMITER (sliding_rate_limiter.py)
# Architecture: Asynchronous Thread-Safe Sliding Window Token Inspector
# =============================================================================
import asyncio
import time
import logging

logger = logging.getLogger("SlidingRateLimiter")

class SlidingRateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.lock = asyncio.Lock()
        self.request_logs = []

    async def acquire(self, domain: str = "global") -> bool:
        """Blocks execution smoothly until a slot opens in the sliding window."""
        async with self.lock:
            while True:
                now = time.time()
                # Prune logs older than our window ceiling
                self.request_logs = [ts for ts in self.request_logs if now - ts < self.window_seconds]
                
                if len(self.request_logs) < self.max_requests:
                    self.request_logs.append(now)
                    return True
                
                # Compute minimum wait boundary before next inspection tick
                sleep_time = self.request_logs[0] + self.window_seconds - now
                if sleep_time > 0:
                    logger.debug(f"Rate ceiling hit for {domain}. Throttling execution for {sleep_time:.4f}s")
                    await asyncio.sleep(sleep_time)

async def test_limiter_suite():
    print("\n\033[1;33m--- RUNNING SLIDING RATE LIMITER TEST SUITE ---\033[0m")
    limiter = SlidingRateLimiter(max_requests=3, window_seconds=1.0)
    
    start_time = time.time()
    for i in range(6):
        await limiter.acquire(domain="target-node")
        print(f"[T+{time.time() - start_time:.2f}s] Task Unit {i+1} cleared security gate.")
        
    duration = time.time() - start_time
    assert duration >= 1.0, f"Rate limiting verification failed! Executed too quickly: {duration:.2f}s"
    print("\033[1;32m[SUCCESS] SlidingRateLimiter suite verified cleanly.\033[0m")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    asyncio.run(test_limiter_suite())
