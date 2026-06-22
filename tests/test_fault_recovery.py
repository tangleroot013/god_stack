import pytest
import asyncio
from unittest.mock import MagicMock, patch
from utils.redis_worker import RedisWorker

@pytest.mark.asyncio
@patch("utils.queue_manager.RedisQueueManager.add_target")
async def test_exponential_backoff_pathway(mock_add):
    # Set base_delay to 0 for instantaneous test evaluation
    worker = RedisWorker(worker_id="test-retry-node", max_retries=2, base_delay=0.0)
    
    mock_task = {"url": "https://simulate-fault.com", "meta": {"retry_count": 0}}
    
    with patch.object(worker.broker.client, "lrem", return_value=1):
        requeued = await worker.handle_mission_fault(mock_task)
        assert requeued is True
        assert mock_add.called
        assert mock_task["meta"]["retry_count"] == 1
