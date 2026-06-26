import pytest
import asyncio
from unittest.mock import MagicMock, patch
from daemon_core import DaemonCore

@pytest.mark.asyncio
@patch("utils.queue_manager.RedisQueueManager.pop_task")
@patch("utils.queue_manager.RedisQueueManager.task_complete")
async def test_worker_polling_consumption(mock_complete, mock_pop):
    # Deliver exactly one payload before falling back to empty states
    mock_pop.side_effect = [{"url": "https://example.com/target", "meta": {}}, None]
    
    core = DaemonCore(max_concurrent_workers=1)
    
    try:
        await asyncio.wait_for(core.main_loop(), timeout=1.0)
    except asyncio.TimeoutError:
        pass

    assert mock_pop.called
    assert mock_complete.called
