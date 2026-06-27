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

async def test_with_target(target_proxy=None):
    scraper = GodScraper(profile_name="high_privacy_profile")
    await scraper.initialize(headless=True, proxy_url=target_proxy)
    try:
        page = await scraper.context.new_page()
        logger.info("Validating fingerprint configuration trace at httpbin.org...")
        await page.goto("https://httpbin.org/ip", timeout=12000)
        content = await page.inner_text("body")
        logger.info(f"\033[1;32m[NODE TRACE CONFIRMED]\033[0m Network Egress Configuration: {content.strip()}")
        return True
    except Exception as e:
        if target_proxy:
            logger.warning(f"Proxy node {target_proxy} failed/timed out: {e}. Attempting clean execution sequence via fallback.")
        else:
            logger.error(f"Fallback direct validation sequence tracking error: {e}")
        return False
    finally:
        await scraper.shutdown()

async def run_stealth_validation():
    print("\n\033[1;36m[STEP 1]\033[0m Harvesting fresh egress node from Scavenger matrix...")
    scavenger = ProxyScavenger()
    proxies = []
    try:
        proxies = await scavenger.run()
    except Exception as e:
        logger.warning(f"Scavenger node processing failure: {e}")
    
    success = False
    if proxies:
        target_proxy = proxies[0]
        logger.info(f"Locking routing vector to Egress Node: {target_proxy}")
        print("\n\033[1;36m[STEP 2]\033[0m Spinning up GodScraper with high_privacy_profile & Proxy Node...")
        success = await test_with_target(target_proxy)
    else:
        logger.warning("No responsive proxy routes discovered by Scavenger.")

    if not success:
        print("\n\033[1;33m[FALLBACK BACKUP LAYER ACTIVATED]\033[0m Executing framework routing validation cleanly via standard direct interface...")
        await test_with_target(None)

if __name__ == "__main__":
    asyncio.run(run_stealth_validation())
