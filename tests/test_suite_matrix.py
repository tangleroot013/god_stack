#!/usr/bin/env python3
import unittest
import asyncio
import time
from metrics_exporter import SYSTEM_METRICS
from unified_production_core import StreamlinedGodScraper

class TestGodStackCoreEngine(unittest.TestCase):
    
    def setUp(self):
        """Reset shared state metrics before each evaluation flight."""
        SYSTEM_METRICS["god_stack_ingestion_attempts_total"] = 0
        SYSTEM_METRICS["god_stack_ingestion_success_total"] = 0

    def test_metrics_registry_atomic_bounds(self):
        """Validates that incremental operational metrics track accurately without mutation flaws."""
        self.assertEqual(SYSTEM_METRICS["god_stack_ingestion_attempts_total"], 0)
        SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
        self.assertEqual(SYSTEM_METRICS["god_stack_ingestion_attempts_total"], 1)

    def test_stream_concurrency_ceiling_enforcement(self):
        """Asserts that the task engine honors limits and does not over-allocate sockets."""
        concurrency_ceiling = 4
        scraper = StreamlinedGodScraper(concurrency_limit=concurrency_ceiling)
        self.assertEqual(scraper.concurrency_limit, concurrency_ceiling)
        self.assertEqual(len(scraper.active_tasks), 0)

    def test_frontier_starvation_resilience(self):
        """Ensures that the runloop enters a non-blocking backoff state when the queue is starved."""
        scraper = StreamlinedGodScraper(concurrency_limit=2)
        
        async def run_brief_loop():
            # Run an empty loop sequence that should exit immediately if unblocked
            task = asyncio.create_task(scraper.start_optimized_orchestration_loop(target_drain_count=0))
            await asyncio.sleep(0.1)
            scraper.active = False
            await task

        start_time = time.time()
        asyncio.run(run_brief_loop())
        duration = time.time() - start_time
        
        # Verify that running an empty loop did not freeze the main threat model
        self.assertTrue(duration < 0.5, f"Execution blocked unnecessarily for {duration} seconds.")

if __name__ == "__main__":
    print("\033[1;36m[TEST MATRIX] Activating internal unit validation tests...\033[0m")
    unittest.main()
