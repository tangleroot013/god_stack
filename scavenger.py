# ==============================================================================
# PROXY SCAVENGER MODULE (scavenger.py)
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
    def __init__(self):
        self.source_url = "https://free-proxy-list.net/"
        self.verified_proxies = []

    async def harvest_raw_list(self) -> list:
        logger.info("Infiltrating public proxy distribution matrix...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.source_url)
                if response.status_code != 200:
                    return []
                soup = BeautifulSoup(response.text, 'html.parser')
                proxies = []
                table = soup.find('table', class_='table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            proxies.append(f"http://{cols[0].text.strip()}:{cols[1].text.strip()}")
                logger.info(f"Harvest complete. Extracted {len(proxies)} raw nodes.")
                return proxies[:20]
        except Exception:
            return []

    async def verify_node(self, proxy_url: str):
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=3.0) as client:
                res = await client.get("http://www.google.com")
                if res.status_code == 200:
                    logger.info(f"\033[1;32m[VERIFIED]\\033[0m Node routing verified: {proxy_url}")
                    self.verified_proxies.append(proxy_url)
        except Exception:
            pass

    async def run(self) -> list:
        raw_list = await self.harvest_raw_list()
        tasks = [self.verify_node(proxy) for proxy in raw_list]
        await asyncio.gather(*tasks)
        logger.info(f"Ecosystem updated. Secured {len(self.verified_proxies)} responsive routes.")
        return self.verified_proxies
