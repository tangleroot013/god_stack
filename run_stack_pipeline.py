#!/usr/bin/env python3
# =============================================================================
# G.O.D. STACK v2.0 CENTRAL PIPELINE CORE (run_stack_pipeline.py)
# Architecture: Defensive Orchestration, Multi-Path Local Import Adjustments
# =============================================================================

import asyncio
import logging
import sys
import os

# Ensure project root AND utils subdirectory are included in the module lookups
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)
sys.path.append(os.path.join(base_dir, "utils"))

# Dynamic import resolution falling back to internal subfolders
try:
    from courlan_router import CourlanRouter
except ImportError:
    from utils.courlan_router import CourlanRouter

try:
    from scavenger import ProxyScavenger
except ImportError:
    from utils.scavenger import ProxyScavenger

try:
    from god_scraper import GodScraper
except ImportError:
    from utils.god_scraper import GodScraper

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[PIPELINE-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PipelineCore")

async def execute_orchestrated_sweep():
    logger.info("Initializing Stack v2.0 Main Processing Loop...")

    # 1. Harvest & Verify Proxies via Scavenger
    scavenger = ProxyScavenger()
    logger.info("Scavenging external egress routing tables...")
    verified_proxies = await scavenger.run()
    
    if not verified_proxies:
        logger.warning("No responsive proxy routes discovered. Falling back to native interface network stack.")
    else:
        logger.info(f"Successfully injected {len(verified_proxies)} active proxy channels into core matrix.")

    # 2. Establish Target Matrices & Filter via Courlan Router
    raw_targets = [
        "https://news.ycombinator.com/news",
        "https://news.ycombinator.com/best"
    ]
    
    sanitized_targets = []
    for url in raw_targets:
        clean_url = CourlanRouter.validate_and_clean(url)
        if clean_url:
            sanitized_targets.append(clean_url)

    logger.info(f"Target validation matrix established. Running jobs: {len(sanitized_targets)}")

    # 3. Fire Asynchronous High Privacy Scraper Engine
    scraper = GodScraper(profile_name="high_privacy_profile")
    try:
        await scraper.initialize(headless=True)
        
        for target in sanitized_targets:
            logger.info(f"Deploying browser core context to target: {target}")
            result = await scraper.scrape(url=target, workflow=[{"action": "scroll"}])
            
            if result.get("status") == "success":
                logger.info(f"\033[1;32m[INGEST SUCCESS]\033[0m Pulled page: '{result.get('title')}' - Content Length: {len(result.get('markdown', ''))} chars.")
            else:
                logger.error(f"Ingest anomaly on endpoint {target}: {result.get('message')}")
                
    except Exception as e:
        logger.critical(f"Pipeline processing execution barrier failure: {str(e)}")
    finally:
        await scraper.shutdown()
        logger.info("Core browser segments reclaimed. Standby mode engaged.")

if __name__ == "__main__":
    try:
        asyncio.run(execute_orchestrated_sweep())
    except KeyboardInterrupt:
        logger.warning("Pipeline execution sequence terminated manually by operator.")
        sys.exit(130)
