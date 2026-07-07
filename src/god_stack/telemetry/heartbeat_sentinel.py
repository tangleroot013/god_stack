#!/usr/bin/env python3
import asyncio
import time
import logging
from typing import Dict

logger = logging.getLogger("GodStack.HeartbeatSentinel")

class HeartbeatSentinel:
    def __init__(self, stale_threshold_seconds: float = 5.0):
        self.worker_registry: Dict[str, float] = {}
        self.stale_threshold = stale_threshold_seconds
        self._lock = asyncio.Lock()

    async def record_pulse(self, worker_id: str):
        async with self._lock:
            self.worker_registry[worker_id] = time.time()

    async def audit_vitality(self) -> Dict[str, str]:
        async with self._lock:
            now = time.time()
            status_report = {}
            for worker_id, last_pulse in self.worker_registry.items():
                if now - last_pulse > self.stale_threshold:
                    status_report[worker_id] = "STALE_OR_HUNG"
                    logger.error(f"Worker node cluster warning: {worker_id} has breached latency threshold.")
                else:
                    status_report[worker_id] = "HEALTHY"
            return status_report
