#!/usr/bin/env python3
# ==============================================================================
# stealth_manager.py – Automated proxy rotation & UA forgery
# ==============================================================================
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;31m%(asctime)s\033[0m | \033[1;37m[STEALTH]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("StealthManager")

class StealthManager:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
        ]
        self.proxies = ["http://123.45.67.89:8080"]

    def get_next_ua(self) -> str:
        ua = random.choice(self.user_agents)
        logger.info(f"🎭 Forged UA: {ua[:40]}...")
        return ua

    def get_next_proxy(self) -> str:
        proxy = random.choice(self.proxies)
        logger.info(f"🔄 Rotated proxy: {proxy}")
        return proxy

if __name__ == "__main__":
    sm = StealthManager()
    print(sm.get_next_ua())
    print(sm.get_next_proxy())
