#!/usr/bin/env python3
import logging
from url_sanitizer import UrlSanitizer

logger = logging.getLogger("PrometheusExporter")

try:
    from prometheus_client import Histogram
    REQUEST_DURATION = Histogram(
        "http_request_duration_seconds",
        "Time spent processing an ingestion request",
        ["url"]
    )
except ImportError:
    # Fail-safe operational stub to prevent runtime execution faults if module is unlinked
    class MockHistogram:
        def labels(self, **kwargs): return self
        def observe(self, amount): pass
    REQUEST_DURATION = MockHistogram()

def observe_request(url: str, elapsed: float):
    """Observes request processing speed while enforcing low label cardinality limits."""
    if not url:
        return
    canonical = UrlSanitizer.normalize(url)
    REQUEST_DURATION.labels(url=canonical).observe(elapsed)
