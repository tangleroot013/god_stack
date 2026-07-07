#!/usr/bin/env python3
import asyncio
import time
import logging
from enum import Enum

logger = logging.getLogger("GodStack.CircuitBreaker")

class BreakerState(Enum):
    CLOSED = 1
    OPEN = 2
    HALF_OPEN = 3

class CircuitBreakerError(Exception):
    pass

class AsyncCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = BreakerState.CLOSED
        self.last_state_change = time.time()
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        async with self._lock:
            now = time.time()
            if self.state == BreakerState.OPEN:
                if now - self.last_state_change > self.recovery_timeout:
                    self.state = BreakerState.HALF_OPEN
                    self.last_state_change = now
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN.")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        async with self._lock:
            now = time.time()
            if exc_type is not None:
                self.failure_count += 1
                if self.state in (BreakerState.CLOSED, BreakerState.HALF_OPEN) and self.failure_count >= self.failure_threshold:
                    self.state = BreakerState.OPEN
                    self.last_state_change = now
            else:
                if self.state == BreakerState.HALF_OPEN:
                    self.state = BreakerState.CLOSED
                    self.failure_count = 0
                elif self.state == BreakerState.CLOSED:
                    self.failure_count = max(0, self.failure_count - 1)
