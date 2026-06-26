# ==============================================================================
# PROXY SCAVENGER MATRIX v2.0.0 (scavenger.py)
# Architecture: Unauthenticated DOM Scraping & Live Validation Engine
# ==============================================================================

import asyncio
import httpx
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;33m%(asctime)s\033[0m | \033[1;31m[SCAVENGER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Scavenger")

class ProxyScavenger:
    """Dynamically harvests and verifies public egress nodes to fuel the engine matrix."""
    def __init__(self):
        self.source_url = "https://free-proxy-list.net/"
        self.verified_proxies = []

    async def harvest_raw_list(self) -> list:
        """Parses raw proxy table blocks directly from public source grids."""
        logger.info("Infiltrating public proxy distribution matrix...")
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self.source_url)
                if response.status_code != 200:
                    logger.error("Failed to harvest raw proxy arrays from source site.")
                    return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            proxies = []
            
            # Target modern free-proxy-list structures
            table = soup.find('table')
            if not table:
                return []
                
            rows = table.find_all('tr')
            for row in rows[1:]:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    if idx := ip.replace('.', '').isdigit():
                        proxies.append(f"http://{ip}:{port}")
            
            logger.info(f"Harvest complete. Extracted {len(proxies)} raw nodes to evaluate.")
            return proxies[:40]
        except Exception as e:
            logger.error(f"Scavenger boundary fault: {str(e)}")
            return []

    async def verify_node(self, proxy_url: str):
        """Tests node latency against a secure reference standard."""
        test_url = "http://www.google.com"
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=2.5) as client:
                res = await client.get(test_url)
                if res.status_code == 200:
                    logger.info(f"\033[1;32m[VERIFIED]\033[0m Node routing verified via: {proxy_url}")
                    self.verified_proxies.append(proxy_url)
        except Exception:
            pass

    async def run(self) -> list:
        raw_list = await self.harvest_raw_list()
        if not raw_list:
            # Fallback array if upstream layout structural break occurs
            return ["http://192.168.1.50:3128"]
        tasks = [self.verify_node(proxy) for proxy in raw_list]
        await asyncio.gather(*tasks)
        logger.info(f"Ecosystem updated. Secured {len(self.verified_proxies)} responsive routes.")
        return self.verified_proxies if self.verified_proxies else ["http://192.168.1.50:3128"]

if __name__ == "__main__":
    print("\n\033[1;35m--- INITIALIZING WILD CARD PROXY SCAVENGER MATRIX ---\033[0m")
    scavenger = ProxyScavenger()
    asyncio.run(scavenger.run())
