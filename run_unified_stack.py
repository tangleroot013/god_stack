#!/usr/bin/env python3
# =============================================================================
# run_unified_stack.py – Unified Pure Python Asynchronous Orchestrator Matrix
# =============================================================================
import asyncio
import logging
import signal
import sys
from url_sanitizer import UrlSanitizer
from scavenger import ProxyScavenger
from god_engine import GodEngine

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;30m%(asctime)s\033[0m | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UnifiedStack")

class UnifiedExecutionMatrix:
    def __init__(self, target_urls: list):
        self.target_urls = target_urls
        self.sanitized_urls = []
        self.scavenger = ProxyScavenger()
        self.engine = GodEngine()
        self.shutdown_event = asyncio.Event()

    def handle_shutdown(self, signum, frame):
        print() # Clear line after ^C
        logger.warning(f"\033[1;31m[SHUTDOWN]\033[0m Intercepted signal ({signum}). Neutralizing loops gracefully...")
        self.shutdown_event.set()

    async def run_url_sanitizer_layer(self):
        logger.info("\033[1;34m[SANITIZER]\033[0m Initializing structural target validation matrix...")
        results = []
        for url in self.target_urls:
            cleaned = UrlSanitizer.normalize(url)
            if cleaned:
                results.append(cleaned)
        self.sanitized_urls = results
        logger.info(f"\033[1;34m[SANITIZER]\033[0m Target alignment complete. Secured {len(self.sanitized_urls)} production routes.")

    async def run_proxy_scavenger_loop(self):
        while not self.shutdown_event.is_set():
            try:
                logger.info("\033[1;33m[SCAVENGER]\033[0m Re-evaluating public proxy distribution matrices...")
                await self.scavenger.run()
                # Cycle every 5 minutes, checking the event loop break flag at 1-second ticks
                for _ in range(300):
                    if self.shutdown_event.is_set():
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[SCAVENGER ANOMALY] Execution error: {e}")
                await asyncio.sleep(10)
        logger.info("\033[1;33m[SCAVENGER]\033[0m Background proxy routine gracefully suspended.")

    async def run_god_engine_loop(self):
        while not self.shutdown_event.is_set():
            try:
                if not self.sanitized_urls:
                    await self.run_url_sanitizer_layer()

                logger.info("\033[1;32m[ENGINE]\033[0m Firing extraction matrix sequences across active hotpaths...")
                
                # Concurrent asynchronous target execution over individual routes via async gather fan-out
                tasks = [self.engine.process_target(url) for url in self.sanitized_urls]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for url, res in zip(self.sanitized_urls, results):
                    if isinstance(res, Exception):
                        logger.error(f"\033[1;31m[ENGINE ANOMALY]\033[0m Boundary fault on {url}: {res}")
                    else:
                        logger.info(f"\033[1;32m[ENGINE]\033[0m Extraction sequence processed cleanly for target: {url}")

                # Throttled execution pause interval polling loop
                for _ in range(60):
                    if self.shutdown_event.is_set():
                        break
                    await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[ENGINE CRITICAL] Context failure: {e}")
                await asyncio.sleep(10)
        logger.info("\033[1;32m[ENGINE]\033[0m Orchestration core successfully offloaded and neutralized.")

    async def bootstrap(self):
        await self.run_url_sanitizer_layer()
        
        scavenger_task = asyncio.create_task(self.run_proxy_scavenger_loop())
        engine_task = asyncio.create_task(self.run_god_engine_loop())

        # Keep running until system intercepts an explicit termination event
        await self.shutdown_event.wait()

        logger.info("Closing active tasks and tearing down network context structures...")
        scavenger_task.cancel()
        engine_task.cancel()

        await asyncio.gather(scavenger_task, engine_task, return_exceptions=True)
        logger.info("\033[1;32m[SUCCESS]\033[0m Refactor matrix lifecycle execution complete. Workspace clean.")

if __name__ == "__main__":
    print("\n\033[1;35m--- INITIALIZING UNIFIED AWESOME-LIST RUNTIME MATRIX ---\033[0m")

    TARGET_GRID = [
        "NEWS.YCOMBINATOR.COM/newest",
        "https://news.ycombinator.com/best"
    ]

    matrix = UnifiedExecutionMatrix(target_urls=TARGET_GRID)

    # Bind operational low-overhead OS signal interception rules
    signal.signal(signal.SIGINT, matrix.handle_shutdown)
    signal.signal(signal.SIGTERM, matrix.handle_shutdown)

    try:
        asyncio.run(matrix.bootstrap())
    except Exception as fatal_err:
        logger.critical(f"Execution matrix suffered unhandled runtime failure: {fatal_err}")
        sys.exit(1)
