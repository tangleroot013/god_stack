import random
import logging
from typing import Dict, List

log = logging.getLogger("AdaptiveThrottler")

class AdaptiveThrottler:
    """Calculates optimal operational delays dynamically using target latency history."""
    
    def __init__(self, min_delay_ms: int = 800, max_delay_ms: int = 5000, variance_percent: int = 15):
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
        self.variance_percent = variance_percent
        # Tracks domain keys to raw lists of latency floats
        self.history: Dict[str, List[float]] = {}

    def record_latency(self, domain: str, latency_ms: float) -> None:
        """Appends a new target network transaction time marker to the tracking window."""
        if domain not in self.history:
            self.history[domain] = []
        self.history[domain].append(latency_ms)
        if len(self.history[domain]) > 10:
            self.history[domain].pop(0)

    def calculate_pacing_delay(self, domain: str) -> int:
        """
        Determines the calculated delay value based on response trends.
        Formula:
            Base = Moving Average * 1.2
            Jitter = Base * (1 +/- Variance)
        """
        domain_history = self.history.get(domain, [])
        if not domain_history:
            base_delay = (self.min_delay_ms + self.max_delay_ms) / 2
        else:
            base_delay = (sum(domain_history) / len(domain_history)) * 1.2

        # Apply random human variance offset profile
        variance_factor = (self.variance_percent / 100.0)
        jitter = random.uniform(-variance_factor, variance_factor)
        final_delay = base_delay * (1.0 + jitter)

        # Clamp calculations within fixed boundary structures
        clamped_delay = max(self.min_delay_ms, min(self.max_delay_ms, final_delay))
        log.debug(f"Target execution window pacing resolved for {domain}: {int(clamped_delay)}ms")
        return int(clamped_delay)
