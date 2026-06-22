import pytest
from utils.metrics_exporter import MetricsExporter, ERROR_RATIO

def test_granular_error_labels():
    exporter = MetricsExporter(port=9998)
    
    # Retrieve base value states
    try:
        base_timeout = ERROR_RATIO.labels(type="timeout")._value.get()
        base_parse = ERROR_RATIO.labels(type="parse")._value.get()
    except AttributeError:
        base_timeout = 0
        base_parse = 0

    # Fire metric updates across distinct categories
    exporter.record_error("timeout")
    exporter.record_error("parse")
    exporter.record_error("parse")

    assert ERROR_RATIO.labels(type="timeout")._value.get() == base_timeout + 1
    assert ERROR_RATIO.labels(type="parse")._value.get() == base_parse + 2
