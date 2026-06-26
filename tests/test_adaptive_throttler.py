import pytest
from utils.adaptive_throttler import AdaptiveThrottler

def test_pacing_default_limits():
    throttler = AdaptiveThrottler(min_delay_ms=1000, max_delay_ms=2000)
    delay = throttler.calculate_pacing_delay("unknown_target.com")
    
    assert 1000 <= delay <= 2000

def test_adaptive_latency_scaling():
    throttler = AdaptiveThrottler(min_delay_ms=200, max_delay_ms=10000, variance_percent=0)
    
    # Anchor target trend baseline to 1000ms latency responses
    for _ in range(5):
        throttler.record_latency("stabilized.org", 1000.0)
        
    delay = throttler.calculate_pacing_delay("stabilized.org")
    
    # Expected: Average (1000) * Scale factor (1.2) = 1200ms
    assert delay == 1200
