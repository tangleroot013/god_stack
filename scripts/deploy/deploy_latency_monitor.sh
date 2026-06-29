#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Constructing Sliding Window Performance Monitor...\033[0m"

cat << 'PYEOF' > latency_monitor.py
import asyncio
import logging
import math

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[PERF-MONITOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PerfMonitor")

class SlidewindowLatencyTracker:
    def __init__(self, window_capacity: int = 4):
        self.window_capacity = window_capacity
        self.latency_buffer = []

    def record_network_delta(self, latency_ms: float):
        print("\n\033[1;32m--- G.O.D. SYSTEM SLIDING-WINDOW LATENCY CALCULATION ---\033[0m")
        self.latency_buffer.append(latency_ms)
        if len(self.latency_buffer) > self.window_capacity:
            self.latency_buffer.pop(0)

        # Compute rolling baseline metrics
        avg_latency = sum(self.latency_buffer) / len(self.latency_buffer)
        logger.info(f"Telemetry captured. Active Sliding Buffer State: {self.latency_buffer}")
        logger.info(f"  Calculated Rolling Average Turnaround Time: \033[1;33m{avg_latency:.2f}ms\033[0m")

async def main():
    tracker = SlidewindowLatencyTracker()
    # Simulate a steady climb in network transit latency bounds
    for tracked_delay in [145.0, 160.0, 295.0, 410.0]:
        tracker.record_network_delta(tracked_delay)
        await asyncio.sleep(0.01)
    print("\n\033[1;32m✔ MODULE 58 MOVING SLIDEWINDOW TELEMETRY READY.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF

echo -e "\033[1;34m[2/2] Running simulated cluster congestion testing sequences...\033[0m"
chmod +x latency_monitor.py
./.venv/bin/python3 latency_monitor.py
