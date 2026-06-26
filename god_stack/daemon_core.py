#!/usr/bin/env python3
# ==============================================================================
# daemon_core.py – Central heartbeat & long-term scheduler
# ==============================================================================
import asyncio
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;35m[DAEMON-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DaemonCore")

class DaemonCore:
    def __init__(self):
        self.schedules = {}
        self.last_run = None

    async def register_job(self, name: str, interval: int, coro):
        self.schedules[name] = {"interval": interval, "coro": coro}
        logger.info(f"Registered job: {name} every {interval}s")

    async def run_forever(self):
        while True:
            now = datetime.now()
            for name, cfg in self.schedules.items():
                if (now - self.last_run).total_seconds() >= cfg["interval"]:
                    logger.info(f"🔄 Executing scheduled job: {name}")
                    await cfg["coro"]()
                    self.last_run = now
            await asyncio.sleep(1)

if __name__ == "__main__":
    core = DaemonCore()
    asyncio.run(core.run_forever())
