import pytest
from god_stack.utils.adaptive_throttler import AdaptiveThrottler

class TestAdaptiveThrottler:
    def test_basic_throttle(self):
        at = AdaptiveThrottler(min_delay=0.01, max_delay=0.1)
        assert at is not None

    def test_delay_increase(self):
        at = AdaptiveThrottler(min_delay=0.01, max_delay=0.1)
        d1 = at.get_delay(success=False)
        d2 = at.get_delay(success=True)
        assert d1 >= d2