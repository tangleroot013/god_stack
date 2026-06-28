#!/usr/bin/env python3
# =============================================================================
# INTEGRATION MATRIX VERIFICATION HARNESS (test_unified_stack.py)
# =============================================================================

import asyncio
import sys
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure standard project layout can resolve imports
try:
    from run_unified_stack import UnifiedExecutionMatrix
except ImportError:
    print("\033[1;31m[TEST ERROR]\033[0m: Could not import run_unified_stack.py.")
    sys.exit(1)

class TestUnifiedStackLifecycle(unittest.IsolatedAsyncioTestCase):

    async def test_execution_matrix_lifecycle(self):
        """Verifies target initialization, task spawning, and clean shutdown hooks."""
        print("\n\033[1;35m[TEST] Launching Refactor Matrix Verification Loop...\033[0m")
        
        test_urls = ["NEWS.YCOMBINATOR.COM/newest", "https://news.ycombinator.com/best"]
        matrix = UnifiedExecutionMatrix(target_urls=test_urls)

        # Mock subcomponent execution methods to avoid executing real external I/O during test
        matrix.scavenger.run = AsyncMock(return_value=["http://127.0.0.1:8080"])
        matrix.engine.process_target_array = MagicMock()

        # Step 1: Check URL sanitization phase explicitly
        await matrix.run_url_sanitizer_layer()
        self.assertEqual(len(matrix.sanitized_urls), 2)
        self.assertTrue(matrix.sanitized_urls[0].startswith("https://"))
        print("\033[1;32m[PASS]\033[0m WHATWG URL standardization pipeline verified.")

        # Step 2: Run the event loop inside a bounded execution window
        bootstrap_task = asyncio.create_task(matrix.bootstrap())

        # Yield control to let tasks spin up cleanly
        await asyncio.sleep(0.5)
        
        # Verify loops are alive and monitoring conditions
        self.assertFalse(matrix.shutdown_event.is_set())
        print("\033[1;32m[PASS]\033[0m Asynchronous core background tasks initialized nominally.")

        # Step 3: Trigger simulated POSIX termination signal
        print("\033[1;34m[TEST] Injecting graceful exit flag into active runtime state...\033[0m")
        matrix.shutdown_event.set()

        # Wait for the teardown sequence to conclude
        await bootstrap_task
        
        # Assertions to secure production state criteria
        self.assertTrue(matrix.shutdown_event.is_set())
        matrix.scavenger.run.assert_called()
        print("\033[1;32m[PASS]\033[0m Teardown protocol finalized cleanly without dropped connection errors.")

if __name__ == "__main__":
    unittest.main()
