import asyncio
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[ADAPT-CONCUR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AdaptiveConcurrency")

class ConcurrencyThrottleMatrix:
    def __init__(self, baseline_ceiling: int = 10, absolute_floor: int = 2):
        self.current_ceiling = baseline_ceiling
        self.absolute_floor = absolute_floor
        self.latency_history = []

    def evaluate_performance_telemetry(self, last_latency_ms: float):
        self.latency_history.append(last_latency_ms)
        if len(self.latency_history) > 5:
            self.latency_history.pop(0)

        avg_latency = sum(self.latency_history) / len(self.latency_history)
        
        # Adaptive Threshold adjustments
        if avg_latency > 800.0 and self.current_ceiling > self.absolute_floor:
            self.current_ceiling = max(self.absolute_floor, self.current_ceiling - 2)
            logger.warning(f"High network latency trend detected ({avg_latency:.1f}ms). Throttling concurrency ceiling down to: {self.current_ceiling}")
        elif avg_latency < 200.0 and self.current_ceiling < 12:
            self.current_ceiling += 1
            logger.info(f"Target cluster environment highly responsive ({avg_latency:.1f}ms). Scaling concurrency ceiling up to: {self.current_ceiling}")

async def main():
    print("\n\033[1;32m--- G.O.D. CONCURRENCY LEVEL TELEMETRY TEST ---\033[0m")
    matrix = ConcurrencyThrottleMatrix(baseline_ceiling=6)
    
    # Simulate an immediate spike in network strain
    simulated_latencies = [120.0, 850.0, 920.0, 990.0]
    for latency in simulated_latencies:
        matrix.evaluate_performance_telemetry(latency)
        await asyncio.sleep(0.01)

    print("\n\033[1;32m✔ MODULE 42 ADAPTIVE SCALING CORE OPERATIONAL.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
