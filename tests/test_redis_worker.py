import pytest
import asyncio
from unittest.mock import MagicMock, patch
from utils.redis_worker import RedisWorker

@pytest.mark.asyncio
@patch("utils.queue_manager.RedisQueueManager.task_complete")
@patch("utils.queue_manager.RedisQueueManager.add_target")
async def test_worker_backoff_and_fault_requeue(mock_add, mock_complete):
    # Initialize a test node worker with zero-delay configurations for immediate execution
    worker = RedisWorker(worker_id="test-node-01", max_retries=1, base_backoff=0.0)
    
    # Test Path 1: Nominal processing loop validation
    nominal_task = {"url": "https://valid-target.com", "meta": {}}
    success = await worker.execute_with_retry(nominal_task)
    assert success is True
    assert mock_complete.called

    # Test Path 2: Fault management loop validation
    failing_task = {"url": "https://fail-target.com", "meta": {"retry_count": 0}}
    with patch.object(worker.broker.client, "lrem", return_value=1):
        failure_handled = await worker.execute_with_retry(failing_task)
        assert failure_handled is False
        assert mock_add.called  # Task must be pushed back to queue for evaluation
