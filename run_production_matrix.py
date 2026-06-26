#!/usr/bin/env python3
# ==============================================================================
# run_production_matrix.py – High-Performance Matrix with Back-Pressure & Telemetry
# ==============================================================================
import asyncio
import time
import logging
import random
from utils.metrics_bridge import telemetry

# Setup structural logging
logging.basicConfig(level=logging.INFO, format="[MATRIX] %(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MatrixEngine")

class ProductionMatrix:
    def __init__(self, max_concurrency=5):
        # Fix 2 & 3: Limit parallel workers using a Semaphore pattern
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.targets = [
            "https://news.ycombinator.com/news",
            "https://news.ycombinator.com/newest",
            "https://news.ycombinator.com/best",
            "https://news.ycombinator.com/ask",
            "https://news.ycombinator.com/show"
        ]

    async def process_pipeline(self, url: str, idx: int):
        """Simulates or drives the headless scraper pipeline with explicit telemetry hooks."""
        start_ts = time.perf_counter()
        success = False
        
        # Acquire slot from back-pressure semaphore
        async with self.semaphore:
            logger.info(f"🚀 [WORKER {idx}] Processing pipeline for target: {url}")
            try:
                # Mocking network/JS engine rendering latency across the matrix pool
                await asyncio.sleep(random.uniform(0.5, 1.8)) 
                
                # Simulate intermittent structural failure for telemetry validation (5% error rate)
                if random.random() < 0.05:
                    raise RuntimeError("Anti-bot handshake or DNS routing matrix rejected connection.")
                    
                success = True
                logger.info(f"✨ [SUCCESS {idx}] Pipeline finalized cleanly for: {url}")
            except Exception as exc:
                logger.error(f"❌ [FAILURE {idx}] Run failed on {url}: {exc}")
            finally:
                # Fix 2: Calculate duration high-precision and flush to JSON
                duration_ms = (time.perf_counter() - start_ts) * 1000
                telemetry.record_job(success=success, duration_ms=duration_ms)

    async def engine_pump(self):
        logger.info(f"⚡ Booting Matrix Engine with Concurrency Cap = {self.semaphore._value}")
        tasks = [self.process_pipeline(url, idx) for idx, url in enumerate(self.targets, start=1)]
        await asyncio.gather(*tasks)
        logger.info("🏁 All queued matrix targets have processed completely.")

if __name__ == "__main__":
    matrix = ProductionMatrix(max_concurrency=3)
    asyncio.run(matrix.engine_pump())
