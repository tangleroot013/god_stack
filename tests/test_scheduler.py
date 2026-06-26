import pytest
import asyncio
from utils.scheduler import AsyncScheduler

@pytest.mark.asyncio
async def test_scheduler_interval_execution():
    # Set hyper-fast testing interval to validate process sequence instantly
    scheduler = AsyncScheduler(interval_seconds=1)
    execution_counter = 0

    async def mock_daemon_job():
        nonlocal execution_counter
        execution_counter += 1

    scheduler.start(mock_daemon_job)
    
    # Wait for execution sequences to cycle twice
    await asyncio.sleep(2.5)
    await scheduler.stop()

    assert execution_counter >= 2
