#!/usr/bin/env python3
# =============================================================================
# G.O.D. STACK PRODUCTION MATRIX DAEMON (run_production_matrix.py)
# Architecture: Bounded Asynchronous Event Loop with Native Telemetry Hook
# =============================================================================

import asyncio
import logging
import signal
import sys

# System Integration Imports
from metrics_exporter import start_telemetry_server, SYSTEM_METRICS
from frontier_manager import Frontier
from url_sanitizer import UrlSanitizer
from god_scraper import GodScraperNode

# Setup structured console layout logging
logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[MATRIX-E2E]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixE2E")

class ProductionIngestionMatrix:
    def __init__(self, max_concurrent_tasks: int = 10, batch_size: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.batch_size = batch_size
        self.is_running = False
        self._loop = None

    async def start(self):
        """Activates the infinite ingestion stream with custom fallbacks."""
        logger.info("⚡ Activating Complete Ingestion to Storage Matrix Loop...")
        self.is_running = True
        self._loop = asyncio.get_running_loop()

        # Phase 1: Initialize the global scraper singleton node (Playwright/Engine)
        if not GodScraperNode.active:
            await GodScraperNode.initialize()

        # Phase 2: Enter persistent orchestration dispatch loop
        while self.is_running:
            try:
                # Harvest targets out of the Frontier
                targets = self._fetch_next_frontier_batch()
                
                if not targets:
                    # Queue cooling-off period if Frontier is entirely exhausted
                    await asyncio.sleep(2)
                    continue

                # Schedule async pipeline tasks concurrently bounded by worker limits
                tasks = [self.ingest_worker_hotpath(url) for url in targets]
                await asyncio.gather(*tasks)

                # Small throttled yield window between generation sweeps
                await asyncio.sleep(0.5)

            except asyncio.CancelledError:
                logger.info("Main worker loop received execution cancellation trigger.")
                break
            except Exception as e:
                logger.error(f"Critical anomaly inside main ingestion loop framework: {str(e)}")
                await asyncio.sleep(5)  # Resilient cooldown buffer before restart attempt

    def _fetch_next_frontier_batch(self) -> list:
        """Queries impending target arrays out of the operational Frontier."""
        try:
            # Safely hook into the scraper node's dynamic target provider
            if hasattr(GodScraperNode, '_get_next_targets'):
                targets = GodScraperNode._get_next_targets(batch_size=self.batch_size)
                if targets:
                    return targets
        except Exception as e:
            logger.warning(f"Unable to read next metrics sweep from frontier manager: {e}")
        
        # Safe seed baseline target fallback to keep pipeline loop alive if unpopulated
        return ["https://github.com/trending"]

    async def ingest_worker_hotpath(self, raw_url: str):
        """Asynchronous hotpath execution pipeline for individual target extraction."""
        async with self.semaphore:
            if not self.is_running:
                return

            # Atomically increment total ingestion attempts via sharing object
            SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
            logger.info(f"▶️ Processing Pipeline Task Frame -> {raw_url}")

            # Step 1: Normalize and sanitize structural schema representation
            normalized_url = UrlSanitizer.normalize(raw_url)
            if not normalized_url:
                logger.warning(f"⏩ Dropping dangerous/corrupted target schema template: {raw_url}")
                SYSTEM_METRICS["god_stack_deduplication_skips_total"] += 1
                return

            # Step 2: Handle processing handoff execution to Scraper & Engine Nodes
            try:
                execution_frame = await GodScraperNode.process_target(normalized_url)
                
                # Verify structural success output criteria
                if execution_frame and execution_frame.get("status") == "SUCCESS":
                    payload_metrics = execution_frame.get("metrics", {})
                    byte_weight = payload_metrics.get("payload_bytes", 0)

                    # Update live tracking variables scraped by Prometheus targets
                    SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
                    SYSTEM_METRICS["god_stack_bytes_processed_total"] += byte_weight
                    
                    logger.info(f"✅ Target Successfully Ingested: {normalized_url} | +{byte_weight} Bytes")
                else:
                    logger.error(f"❌ Pipeline runtime error reported for target route: {normalized_url}")
                    
            except Exception as worker_error:
                logger.error(f"🚨 Target Boundary Exception over {normalized_url}: {str(worker_error)}")

    def shutdown(self):
        """Gracefully tears down tasks, loop tracking state, and browsers."""
        logger.info("Initiating structural production shutdown protocols...")
        self.is_running = False

def handle_exit_signals(matrix_instance):
    """Binds OS termination signals cleanly to prevent frozen browser loops."""
    logger.info("Systemd termination request caught. Commencing graceful teardown...")
    matrix_instance.shutdown()
    
    # Schedule the scraper's native cleanup asynchronously
    if matrix_instance._loop and matrix_instance._loop.is_running():
        asyncio.ensure_future(GodScraperNode.shutdown(), loop=matrix_instance._loop)

async def main():
    # 1. Start the inline Prometheus Exposition telemetry loop on Port 8000
    start_telemetry_server(port=8000)

    # 2. Instantiate and launch the Core Ingestion Orchestrator Matrix
    matrix = ProductionIngestionMatrix(max_concurrent_tasks=10, batch_size=5)

    # 3. Register standard POSIX signal traps for systemd daemon management
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: handle_exit_signals(matrix))
        except NotImplementedError:
            pass # Resilient safe layout bypass for testing under varying platforms

    try:
        await matrix.start()
    finally:
        logger.info("[GOD-ENGINE] ⏳ Cycle complete. Retention hold active: Keeping port 8000 open for Prometheus...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Matrix process manually interrupted. Exiting.")
        sys.exit(0)
