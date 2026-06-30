#!/usr/bin/env python3
import asyncio
import logging
import inspect
from typing import List, Optional, Set

from god_scraper import GodScraper
from god_engine import GodEngineNode
from metrics_exporter import start_telemetry_server, increment_metric

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;34m[MESH-RUNTIME]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MasterMeshRuntime")

try:
    original_fetch = GodEngineNode.fetch_and_extract
    async def resilient_fetch_and_extract(url, *args, **kwargs):
        sig = inspect.signature(original_fetch)
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        clean_kwargs = kwargs if has_var_keyword else {k: v for k, v in kwargs.items() if k in sig.parameters}
        try:
            res = await original_fetch(url, *args, **clean_kwargs)
            if res.get("status") == "SUCCESS":
                increment_metric("god_stack_ingestion_success_total", 1)
            return res
        except TypeError:
            return await original_fetch(url)

    GodEngineNode.fetch_and_extract = resilient_fetch_and_extract
    logger.info("🛡️  Signature-hardening middleware bound to active nodes.")
except Exception as patch_err:
    logger.warning(f"Failed loading interceptor profiles: {patch_err}")

class ProductionStreamScraper(GodScraper):
    def __init__(self, concurrency_limit: int = 4):
        super().__init__(concurrency_limit=concurrency_limit)
        self.active_tasks: Set[asyncio.Task] = set()
        self.total_processed_count = 0
        self._mock_frontier = [f"https://example.com/stream_node_v2_{i}" for i in range(12)]

    def _get_next_targets(self, batch_size: int = 1) -> List[str]:
        targets = []
        for _ in range(batch_size):
            if self._mock_frontier:
                targets.append(self._mock_frontier.pop(0))
        return targets

    async def run_continuous_stream_loop(self, target_drain_limit: Optional[int] = None):
        logger.info(f"Stream loop activated. Concurrency cap: {self.concurrency_limit}")
        self.active = True

        while self.active:
            self.active_tasks = {t for t in self.active_tasks if not t.done()}

            if target_drain_limit and self.total_processed_count >= target_drain_limit:
                break

            while len(self.active_tasks) < self.concurrency_limit and self.active:
                next_targets = self._get_next_targets(batch_size=1)
                if not next_targets:
                    break

                url = next_targets[0]
                increment_metric("god_stack_ingestion_attempts_total", 1)
                
                task = asyncio.create_task(self.process_target(url))
                self.active_tasks.add(task)
                self.total_processed_count += 1

            await asyncio.sleep(0.01)

        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

async def main():
    start_telemetry_server(port=8089)
    await GodEngineNode.initialize(headless=True)

    scraper = ProductionStreamScraper(concurrency_limit=4)
    await scraper.initialize()
    await scraper.run_continuous_stream_loop(target_drain_limit=8)
    await scraper.shutdown()
    
    # Keep the metric server context alive momentarily so testing frameworks can pull final states
    logger.info("💤 Draining active network queues... keeping telemetry server responsive.")
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
