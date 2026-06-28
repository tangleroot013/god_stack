import asyncio
import logging
from scavenger import ProxyScavenger
from god_scraper import GodScraper

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[TEST-RUNNER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TestRunner")

async def run_stealth_validation():
    print("\n\033[1;36m[STEP 1]\033[0m Harvesting fresh egress node from Scavenger matrix...")
    scavenger = ProxyScavenger()
    proxies = await scavenger.run()
    
    if not proxies:
        logger.error("No active proxy nodes returned. Aborting stealth run.")
        return
        
    target_proxy = proxies[0]
    logger.info(f"Locking targeting vector to Egress Node: {target_proxy}")

    print("\n\033[1;36m[STEP 2]\033[0m Spinning up GodScraper Node...")
    # Initialize using native signature
    scraper = GodScraper(concurrency_limit=2)
    await scraper.initialize()
    
    print("\n\033[1;36m[STEP 3]\033[0m Dispatching production process route to httpbin.org...")
    try:
        # Route action directly through the scraper engine execution pipeline
        await scraper.process_target("https://httpbin.org/ip")
        logger.info("\033[1;32m[NODE TRACE EXECUTION COMPLETE]\033[0m Review metrics daemon output for side-effects.")
    except Exception as e:
        logger.warning(f"Processing execution failed: {e}")
    finally:
        await scraper.shutdown()

if __name__ == "__main__":
    asyncio.run(run_stealth_validation())
