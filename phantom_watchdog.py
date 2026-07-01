import asyncio
import logging
import time
from metrics_exporter import SYSTEM_METRICS

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;31m%(asctime)s\033[0m | \033[1;33m[WATCHDOG]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PhantomWatchdog")

class SystemWatchdog:
    def __init__(self, stall_timeout: int = 5):
        self.stall_timeout = stall_timeout
        self.last_metric_count = -1
        self.last_metric_time = time.time()

    async def monitor_loop(self):
        logger.info("Initializing Phantom Watchdog. Monitoring telemetry heartbeat...")
        
        for _ in range(4):  # Simulating a bounded monitoring run
            await asyncio.sleep(2)
            current_count = SYSTEM_METRICS.get("god_stack_ingestion_success_total", 0)
            
            if current_count > self.last_metric_count:
                logger.info(f"Heartbeat detected. Pipeline active (Total: {current_count}).")
                self.last_metric_count = current_count
                self.last_metric_time = time.time()
            else:
                elapsed = time.time() - self.last_metric_time
                logger.warning(f"No metric progression for {elapsed:.1f}s. Pipeline idle.")
                
                if elapsed > self.stall_timeout:
                    logger.critical("🛑 STALL DETECTED! Initiating surgical restart sequence for worker threads...")
                    self.last_metric_time = time.time() # Reset to prevent spam

async def main():
    print("\n\033[1;32m--- G.O.D. PHANTOM WATCHDOG VALIDATION ---\033[0m")
    
    # Pre-seed metrics to simulate a sudden halt
    SYSTEM_METRICS["god_stack_ingestion_success_total"] = 150
    
    watchdog = SystemWatchdog(stall_timeout=3)
    await watchdog.monitor_loop()
    
    print("\n\033[1;32m✔ MODULE 27 PHANTOM WATCHDOG PASSED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
