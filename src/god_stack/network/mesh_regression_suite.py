#!/usr/bin/env python3
import unittest
import asyncio
import time
import sqlite3
from metrics_exporter import increment_metric, sync_from_database, SYSTEM_METRICS, init_persistent_db
from master_mesh_runtime import ProductionStreamScraper

class TestGodStackMeshIntegrity(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect("god_stack_vfs.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS telemetry")
        conn.commit()
        conn.close()
        init_persistent_db()
        for k in SYSTEM_METRICS:
            SYSTEM_METRICS[k] = 0

    def test_openmetrics_atomic_mutations(self):
        increment_metric("god_stack_ingestion_attempts_total", 5)
        sync_from_database()
        self.assertEqual(SYSTEM_METRICS["god_stack_ingestion_attempts_total"], 5)

    def test_concurrency_envelope_ceiling(self):
        scraper = ProductionStreamScraper(concurrency_limit=3)
        self.assertEqual(scraper.concurrency_limit, 3)

    def test_deadlock_resilience(self):
        scraper = ProductionStreamScraper(concurrency_limit=2)
        async def mock_pass():
            await scraper.initialize()
            task = asyncio.create_task(scraper.run_continuous_stream_loop(target_drain_limit=0))
            await asyncio.sleep(0.02)
            scraper.active = False
            await task
            await scraper.shutdown()
            
        start = time.time()
        asyncio.run(mock_pass())
        self.assertTrue((time.time() - start) < 0.5)

if __name__ == "__main__":
    print("\033[1;36m[REGRESSION SUITE] Executing regression test layers...\033[0m")
    unittest.main()
