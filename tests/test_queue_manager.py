import pytest
import json
from unittest.mock import MagicMock, patch
from utils.queue_manager import RedisQueueManager

@patch("redis.Redis")
def test_broker_deduplication_and_handling(mock_redis_class):
    mock_client = MagicMock()
    mock_redis_class.return_value = mock_client
    
    broker = RedisQueueManager()
    
    # Configure mock responses for Set manipulation
    mock_client.sadd.side_effect = [1, 0]  # First insert succeeds, second hits duplicate block
    
    assert broker.add_target("https://target-alpha.com") is True
    assert broker.add_target("https://target-alpha.com") is False
    
    # Configure pop execution parameters
    mock_task = {"url": "https://target-alpha.com", "meta": {}}
    mock_client.brpoplpush.return_value = json.dumps(mock_task)
    
    popped = broker.pop_task(timeout=1)
    assert popped["url"] == "https://target-alpha.com"
