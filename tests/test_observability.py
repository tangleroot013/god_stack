import pytest
from unittest.mock import MagicMock
from utils.metrics_exporter import MetricsExporter, JOBS_PROCESSED

def test_metrics_counter_incrementation():
    exporter = MetricsExporter(port=9999)
    
    # Snapshot starting state sample counts
    try:
        start_val = JOBS_PROCESSED.labels(status="success")._value.get()
    except AttributeError:
        start_val = 0
        
    exporter.record_job(success=True)
    
    end_val = JOBS_PROCESSED.labels(status="success")._value.get()
    assert end_val == start_val + 1
