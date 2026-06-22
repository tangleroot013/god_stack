import pytest
import asyncio
from unittest.mock import MagicMock, patch
from utils.metrics_exporter import MetricsExporter

@pytest.mark.asyncio
@patch("utils.queue_manager.RedisQueueManager")
@patch("utils.monitor_relay.MonitorRelay")
async def test_metrics_extraction_and_broadcast(mock_relay, mock_broker):
    # Setup mock data extraction calls
    mock_broker.client.llen.side_effect = [10, 2]
    mock_broker.client.scard.return_value = 100
    mock_broker.pending_queue = "test_pending"
    mock_broker.active_processing = "test_active"
    mock_broker.seen_set = "test_seen"

    exporter = MetricsExporter(broker=mock_broker, relay=mock_relay, check_interval=1)
    exporter.start()
    
    # Wait briefly for one tick cycle loop pass
    await asyncio.sleep(1.2)
    await exporter.stop()

    assert mock_relay.broadcast.called
    event, payload = mock_relay.broadcast.call_args[0]
    assert event == "cluster_telemetry"
    assert payload["pending_tasks"] == 10
    assert payload["active_workers"] == 2
