#!/usr/bin/env python3
import asyncio
import logging
import sys
import aiohttp
from typing import List, Optional

from god_scraper import GodScraper
from god_engine import GodEngineNode
from metrics_exporter import start_telemetry_server, SYSTEM_METRICS
from frontier_manager import Frontier

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[CORE-ENGINE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ProductionCore")

class StreamlinedGodScraper(GodScraper):
    def __init__(self, concurrency_limit: int = 5):
        super().__init__(concurrency_limit=concurrency_limit)
        self.active_tasks = set()

    async def start_optimized_orchestration_loop(self, target_drain_count: Optional[int] = None):
        """Drains tasks concurrently without batch head-of-line blocks."""
        logger.info(f"Task streaming online. Concurrency ceiling: {self.concurrency_limit}")
        self.active = True
        processed = 0

        while self.active:
            self.active_tasks = {t for t in self.active_tasks if not t.done()}
            
            if target_drain_count and processed >= target_drain_count:
                logger.info("Target execution limit reached. Transitioning to drain...")
                break

            while len(self.active_tasks) < self.concurrency_limit and self.active:
                next_targets = self._get_next_targets(batch_size=1)
                if not next_targets:
                    break

                target_url = next_targets[0]
                SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
                
                task = asyncio.create_task(self.process_target(target_url))
                self.active_tasks.add(task)
                processed += 1

            if not self.active_tasks:
                await asyncio.sleep(0.05)
                continue

            await asyncio.sleep(0.01)

        if self.active_tasks:
            logger.info(f"Emptying runtime pipeline. Waiting on {len(self.active_tasks)} workers...")
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

async def run_network_audit():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("https://httpbin.org/headers", timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    ua = data.get("headers", {}).get("User-Agent", "None")
                    logger.info(f"Reflected Edge User-Agent: {ua}")
                    if "Python" in ua or "aiohttp" in ua:
                        logger.warning("🚨 Structural Leak Alert: Raw execution headers exposed.")
                else:
                    logger.error(f"Egress audit failure status code: {resp.status}")
        except Exception as e:
            logger.error(f"Reflective verification channel offline: {e}")

async def main():
    start_telemetry_server(port=8086)
    await GodEngineNode.initialize(headless=True)
    await run_network_audit()

    scraper = StreamlinedGodScraper(concurrency_limit=5)
    await scraper.initialize()
    
    # Populate simulation queue
    for i in range(15):
        Frontier.add_url(f"https://example.com/target_node_{i}")

    await scraper.start_optimized_orchestration_loop(target_drain_count=15)
    await scraper.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
