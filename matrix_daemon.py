# ==============================================================================
# INTEGRATED DAEMON WATCHDOG (matrix_daemon.py)
# Architecture: Continuous Process Monitoring & High-Level Lifecycle Control
# ==============================================================================
import asyncio
import signal
import sys
import logging
from matrix_orchestrator import CoreMatrixOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;31m%(asctime)s\033[0m | \033[1;33m[SCAVENGER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixDaemon")

class MatrixDaemon:
    def __init__(self):
        self.orchestrator = CoreMatrixOrchestrator()
        self.is_running = True

    def _handle_shutdown(self, signum, frame):
        """Intercepts OS signals to flip the runtime engine flags to an exit state."""
        logger.warning(f"\nIntercepted shutdown signal ({signum}). Terminating daemon boundaries cleanly...")
        self.is_running = False

    async def start_engine_loop(self, seed_urls: list):
        print("\n--- BOOTING INTEGRATED CONTINUOUS DAEMON MASTER PROCESS ---")
        
        # Register graceful termination handlers
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(self._shutdown_sequence()))
            except NotImplementedError:
                # Fallback for platforms missing full signal loop binding support
                signal.signal(sig, self._handle_shutdown)

        # Initialize the underlying layers (storage & initial proxies)
        await self.orchestrator.initialize_system()
        
        # Seed the matrix if initial targets are supplied
        if seed_urls:
            await self.orchestrator.storage.seed_job_matrix(seed_urls)

        # Continuous target sweep execution loop
        while self.is_running:
            try:
                job_executed = await self.orchestrator.process_next_job()
                
                if not job_executed:
                    logger.info("Job queue idle. Resting thread execution window for 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    # Politeness spacing between queue runs
                    await asyncio.sleep(2)
            except Exception as loop_error:
                logger.error(f"Fault inside daemon lifecycle sweep: {str(loop_error)}")
                await asyncio.sleep(5)

        await self._final_cleanup()

    async def _shutdown_sequence(self):
        logger.warning("Intercepted shutdown signal. Terminating daemon boundaries cleanly...")
        self.is_running = False

    async def _final_cleanup(self):
        logger.info("Cleaning daemon runtime execution frames...")
        # Check if orchestrator has an active scraper context to close out
        if hasattr(self.orchestrator, 'scraper') and self.orchestrator.scraper:
            await self.orchestrator.scraper.shutdown()
        logger.info("\033[1;32m[SHUTDOWN COMPLETE]\033[0m Daemon context exited safely.")
        sys.exit(0)

if __name__ == "__main__":
    TEST_MATRIX = [
        "https://news.ycombinator.com/news",
        "https://news.ycombinator.com/best?utm_source=tracker_id",
        "https://news.ycombinator.com/newest"
    ]
    daemon = MatrixDaemon()
    try:
        asyncio.run(daemon.start_engine_loop(TEST_MATRIX))
    except (KeyboardInterrupt, SystemExit):
        pass
