#!/usr/bin/env python3
import asyncio
import logging
from typing import List, Optional

logger = logging.getLogger("GodStack.ProxyRotator")

class ProxyRotator:
    def __init__(self, initial_proxies: List[str], quarantine_time: float = 30.0):
        self.active_pool = initial_proxies.copy()
        self.quarantined = {}
        self.quarantine_time = quarantine_time
        self._lock = asyncio.Lock()
        self._index = 0

    async def get_proxy(self) -> Optional[str]:
        async with self._lock:
            if not self.active_pool:
                logger.warning("Proxy pool exhausted. Running direct.")
                return None
            proxy = self.active_pool[self._index % len(self.active_pool)]
            self._index += 1
            return proxy

    async def report_failure(self, proxy: str):
        async with self._lock:
            if proxy in self.active_pool:
                self.active_pool.remove(proxy)
                self.quarantined[proxy] = asyncio.get_event_loop().time()
                logger.info(f"Proxy {proxy} quarantined.")
                asyncio.create_task(self._auto_recover(proxy))

    async def _auto_recover(self, proxy: str):
        await asyncio.sleep(self.quarantine_time)
        async with self._lock:
            if proxy in self.quarantined:
                del self.quarantined[proxy]
                self.active_pool.append(proxy)
                logger.debug(f"Proxy {proxy} recovered and returned to active pool.")
