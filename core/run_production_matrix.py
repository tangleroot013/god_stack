#!/usr/bin/env python3
# ==============================================================================
# MASTER PRODUCTION CONCURRENCY ENGINE (run_production_matrix.py)
# Architecture: Fully Integrated Async Loop, Frontier Routing & Anti-Bot Sentinel
# ==============================================================================

import os
import sys
import json
import asyncio
import logging
from typing import List

# Structural adjustments to ensure parent paths resolve cleanly across cross-imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.url_sanitizer import UrlSanitizer
    from utils.courlan_router import CourlanRouter
    from utils.scavenger import Scavenger
    from daemons.captcha_handler import CaptchaHandler
    from engines.god_engine import GodEngine
except ImportError as e:
    logging.error(f"Ecosystem cross-import failed: {str(e)}")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[CORE-ORCHESTRATOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MasterMatrix")

class ProductionMatrixCoordinator:
    def __init__(self, target_queue: List[str]):
        self.raw_queue = target_queue
        self.sanitized_queue = []
        self.proxy_pool = []
        self.captcha_sentinel = CaptchaHandler()
        self.execution_engine = GodEngine()

    async def run_pipeline(self):
        logger.info("--- STARTING PRODUCTION CYCLE ---")
        
        # 1. Activate Egress Node Acquisition Layer
        logger.info("Spawning background egress proxy harvesting engine...")
        scavenger = Scavenger()
        try:
            # Gather valid responsive routes
            self.proxy_pool = await scavenger.run()
            logger.info(f"Egress grid provisioned. Secured {len(self.proxy_pool)} functional proxy circuits.")
        except Exception as proxy_fault:
            logger.error(f"Proxy matrix pipeline dropped out: {str(proxy_fault)}. Falling back to local interfaces.")

        # 2. Execute Frontier URL Scrubbing Matrix
        logger.info("Passing runtime queue profiles through sanitation filters...")
        for url in self.raw_queue:
            normalized = UrlSanitizer.normalize(url)
            purified = CourlanRouter.validate_and_clean(normalized)
            if purified:
                self.sanitized_queue.append(purified)
        
        logger.info(f"Frontier filter execution finished. Active track list: {len(self.sanitized_queue)} items.")

        # 3. Simulate and Route via Scraping Loop
        if not self.sanitized_queue:
            logger.warning("Pipeline context contains zero routable links. Aborting core execution loop.")
            return

        logger.info("Commencing batch process distribution across engine array...")
        # Inject dynamic proxy routing from the scavenged pool into our standard execution engine if available
        if self.proxy_pool:
            chosen_proxy = self.proxy_pool[0]
            logger.info(f"Binding matrix execution frame to proxy route -> {chosen_proxy}")
            self.execution_engine.scraper.proxies = {"http": chosen_proxy, "https": chosen_proxy}

        # Run the sequential processor matrix
        self.execution_engine.process_target_array(self.sanitized_queue)
        
        logger.info("\033[1;32m[CYCLE COMPLETE]\033[0m All data pipelines serialized cleanly to outputs/.")

if __name__ == "__main__":
    # Sample multi-tiered target queue testing parameters
    TEST_QUEUE = [
        "NEWS.YCOMBINATOR.COM/newest/",
        "https://news.ycombinator.com/best?utm_source=tracker&id=999#anchor",
        "//news.ycombinator.com/ask"
    ]
    
    coordinator = ProductionMatrixCoordinator(TEST_QUEUE)
    asyncio.run(coordinator.run_pipeline())
