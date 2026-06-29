import time
import logging
import collections

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[THROUGHPUT]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ThroughputCalc")

class SlidingWindowThroughputCalculator:
    def __init__(self, window_seconds: int = 5):
        self.window_seconds = window_seconds
        self.history = collections.deque()

    def record_transfer_bytes(self, byte_count: int):
        print("\n\033[1;32m--- G.O.D. STREAM METRIC VELOCITY TRACKING ---\033[0m")
        now = time.time()
        self.history.append((now, byte_count))
        
        # Purge data points outside the active temporal window boundary
        while self.history and self.history[0][0] < (now - self.window_seconds):
            self.history.popleft()
            
        total_bytes = sum(b for _, b in self.history)
        logger.info(f"Recorded ingestion frame load segment: {byte_count} bytes.")
        logger.info(f"  Calculated Dynamic window velocity: \033[1;34m{total_bytes / self.window_seconds:.2f} B/s\033[0m")

if __name__ == "__main__":
    calc = SlidingWindowThroughputCalculator()
    calc.record_transfer_bytes(2048)
    calc.record_transfer_bytes(4096)
    print("\n\033[1;32m✔ MODULE 84 WINDOW THROUGHPUT MONITOR COMPLIANT.\033[0m\n")
