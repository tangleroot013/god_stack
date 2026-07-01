#!/usr/bin/env python3
import asyncio
import time
import logging

logger = logging.getLogger("GodStack.RateLimiter")

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: float = 1.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests_timestamps = []
        self._lock = asyncio.Lock()

    async def acquire(self, client_id: str = "default"):
        async with self._lock:
            while True:
                now = time.time()
                self.requests_timestamps = [t for t in self.requests_timestamps if now - t < self.window_seconds]
                
                if len(self.requests_timestamps) < self.max_requests:
                    self.requests_timestamps.append(now)
                    logger.debug(f"[{client_id}] Token acquired. ({len(self.requests_timestamps)}/{self.max_requests})")
                    return True
                
                sleep_time = self.requests_timestamps[0] + self.window_seconds - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
