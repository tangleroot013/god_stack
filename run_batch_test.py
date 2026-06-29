import asyncio
import logging
from orchestrator import GodOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[BATCH-TEST]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BatchTest")

TEST_URLS = [
    "https://example.com",
    "https://httpbin.org/html",
    "https://news.ycombinator.com"
]

async def run_batch():
    logger.info("Initializing Orchestrator matrix for batch testing...")
    orchestrator = GodOrchestrator(use_proxies=False)
    await orchestrator.initialize_matrix()

    logger.info(f"Loaded {len(TEST_URLS)} targets. Commencing batch execution.")
    
    for url in TEST_URLS:
        logger.info(f"Locking targeting vector to: {url}")
        result = await orchestrator.execute_mission(url)
        
        if result.get("status") == "success":
            logger.info(f"Extraction successful for {url} | Message: {result.get('message')}")
        else:
            logger.warning(f"Mission failed or blocked for {url} | Reason: {result.get('message')}")
        
        await asyncio.sleep(1.5)
    
    logger.info("Batch execution sequence complete. Triggering graceful teardown...")
    if hasattr(orchestrator.engine, 'shutdown'):
        await orchestrator.engine.shutdown()
        
    logger.info("Teardown verified. Subsystems deactivated safely.")

if __name__ == "__main__":
    try:
        asyncio.run(run_batch())
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user. Triggering emergency halt.")
    except Exception as e:
        logger.error(f"Fatal pipeline collapse: {e}")
