import pytest
import asyncio
from god_stack.utils.metrics_exporter import MetricsExporter

@pytest.mark.asyncio
async def test_metrics_broadcast_telemetry():
    exporter = MetricsExporter(port=9999)
    
    # Simulate cluster telemetry emission
    exporter.record_job(success=True)
    exporter.record_job(success=True)
    exporter.record_job(success=False)
    
    # Validate that the internal counter reflects the correct distribution
    assert exporter.jobs_processed["success"] == 2
    assert exporter.jobs_processed["failure"] == 1
    assert exporter.active_workers == 0