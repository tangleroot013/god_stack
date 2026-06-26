#!/usr/bin/env python3
# ==============================================================================
# daemon_core.py – Central Heartbeat with Automated Resource Snapshotting
# ==============================================================================
import asyncio
import logging
import time
import psutil
from datetime import datetime
from utils.metrics_db import _exec, record_worker

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;35m[DAEMON-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DaemonCore")

class DaemonCore:
    def __init__(self):
        self.schedules = {}
        self.last_run = {}

    async def register_job(self, name: str, interval: int, coro):
        self.schedules[name] = {"interval": interval, "coro": coro}
        self.last_run[name] = datetime.min
        logger.info(f"Registered workflow: {name} [Target Frequency: Every {interval}s]")

    async def run_forever(self):
        logger.info("Initializing multi-threaded scheduling telemetry frame...")
        while True:
            start_time = time.time()
            now = datetime.now()
            
            for name, cfg in self.schedules.items():
                if (now - self.last_run[name]).total_seconds() >= cfg["interval"]:
                    logger.info(f"🔄 Spawning execution thread: {name}")
                    self.last_run[name] = now
                    try:
                        await cfg["coro"]()
                        record_worker(name, "success")
                    except Exception as execution_fault:
                        logger.error(f"❌ Structural exception caught on worker '{name}': {str(execution_fault)}")
                        record_worker(name, "failure")

            # Collect resource telemetry metrics
            mem = psutil.Process().memory_info().rss
            duration = time.time() - start_time
            
            try:
                _exec(
                    "INSERT INTO daemon_loop (ts, duration, memory_bytes) VALUES (?,?,?)",
                    (int(start_time), duration, mem),
                )
            except Exception as db_err:
                logger.error(f"Telemetry logging failed: {str(db_err)}")
            
            await asyncio.sleep(1)
