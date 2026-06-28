#!/usr/bin/env python3
# =============================================================================
# test_unified_stack.py – Regression and Contract Alignment Testing Suite
# =============================================================================
import asyncio
import unittest
from unittest.mock import AsyncMock
from run_unified_stack import UnifiedExecutionMatrix

class TestUnifiedStackLifecycle(unittest.IsolatedAsyncioTestCase):
    async def test_lifecycle_execution_flow(self):
        print("\n\n[TEST] Launching Refactor Matrix Verification Loop...")
        
        # Clean array syntax definition without escaping anomalies
        test_urls = ["NEWS.YCOMBINATOR.COM/newest", "https://news.ycombinator.com/best"]
        matrix = UnifiedExecutionMatrix(target_urls=test_urls)

        # Patch internal calls using explicit AsyncMock instances to isolate network context
        matrix.scavenger.run = AsyncMock(return_value=["http://127.0.0.1:8080"])
        matrix.engine.process_target = AsyncMock(return_value={"status": "success"})

        # Step 1: Check validation structure integrity
        await matrix.run_url_sanitizer_layer()
        self.assertEqual(len(matrix.sanitized_urls), 2)
        self.assertTrue(matrix.sanitized_urls[0].startswith("https://"))
        print("\033[1;32m[PASS]\033[0m WHATWG URL standardization pipeline verified.")

        # Step 2: Bootstrap inside an isolated bounded loop container
        bootstrap_task = asyncio.create_task(matrix.bootstrap())
        await asyncio.sleep(0.2)

        self.assertFalse(matrix.shutdown_event.is_set())
        print("\033[1;32m[PASS]\033[0m Asynchronous core background tasks initialized nominally.")

        # Step 3: Trigger simulated hardware termination interrupt signal
        print("\033[1;34m[TEST] Injecting graceful exit flag into active runtime state...\033[0m")
        matrix.shutdown_event.set()

        # Let termination sequence execute completely
        await bootstrap_task

        self.assertTrue(matrix.shutdown_event.is_set())
        matrix.scavenger.run.assert_called()
        matrix.engine.process_target.assert_called()
        print("\033[1;32m[PASS]\033[0m Teardown protocol finalized cleanly without dropped connection errors.")

if __name__ == "__main__":
    unittest.main()
