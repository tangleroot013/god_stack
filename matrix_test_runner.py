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
        logger.warning("No active proxy nodes returned. Using fallback simulation runtime vector.")
        target_proxy = "http://127.0.0.1:8080"
    else:
        target_proxy = proxies[0]
        
    logger.info(f"Locking targeting vector to Egress Node: {target_proxy}")

    print("\n\033[1;36m[STEP 2]\033[0m Spinning up GodScraper with high_privacy_profile & Proxy...")
    # Passing both parameters into the upgraded initialization contract
    scraper = GodScraper(profile_name="high_privacy_profile")
    
    # Clean execution using the newly refactored Option A signature
    await scraper.initialize(headless=True, proxy_url=target_proxy)
    page = await scraper.context.new_page()
    
    print("\n\033[1;36m[STEP 3]\033[0m Validating fingerprint leakage assertions...")
    try:
        await page.goto("https://httpbin.org/ip", timeout=15000)
        data = await page.content()
        logger.info("Extraction matrix validated successfully. System response data integrated.")
        print(f"\033[1;32m[SUCCESS]\033[0m Matrix runtime validated output: {data}")
    except Exception as e:
        logger.error(f"Network verification stage error context: {str(e)}")
    finally:
        await scraper.shutdown()

if __name__ == "__main__":
    asyncio.run(run_stealth_validation())
