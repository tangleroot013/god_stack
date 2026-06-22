import pytest
import asyncio
from unittest.mock import MagicMock, patch
from daemon_core import DaemonCore

@pytest.mark.asyncio
@patch("utils.queue_manager.RedisQueueManager.pop_task")
@patch("utils.queue_manager.RedisQueueManager.task_complete")
async def test_daemon_polling_and_worker_throttling(mock_complete, mock_pop):
    # Setup test bounds to feed exactly 1 mock task then terminate
    mock_pop.side_effect = [{"url": "https://test-node-target.org"\}, None]
    
    core = DaemonCore(max_concurrent_workers=2)
    
    # Run loop worker iteration pass via timeout escape mechanism
    try:
        await asyncio.wait_for(core.main_loop(), timeout=1.5)
    except asyncio.TimeoutError:
        pass

    assert mock_pop.called
    assert mock_complete.called
