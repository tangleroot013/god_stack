import asyncio
import json
import logging
import yaml
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[GOD-ENGINE]\033[0m %(message)s"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, profile_name: str = "default_profile", profile_path: str = "stealth_profiles.yaml"):
        self.profile_name = profile_name
        self.profile = self._load_profile(profile_path, profile_name)
        self.playwright = None
        self.browser = None
        self.context = None

    def _load_profile(self, path: str, name: str) -> Dict[str, Any]:
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)
                return config.get(name, config.get("default_profile", {}))
        except Exception:
            return {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async def initialize(self, headless: bool = True, proxy_url: Optional[str] = None):
        self.playwright = await async_playwright().start()
        
        # Structure the proxy payload cleanly for Playwright if provided
        proxy_config = {"server": proxy_url} if proxy_url else None
        
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            proxy=proxy_config,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--ignore-certificate-errors'
            ]
        )
        
        self.context = await self.browser.new_context(
            user_agent=self.profile.get("user_agent"),
            viewport=self.profile.get("viewport", {"width": 1920, "height": 1080}),
            locale=self.profile.get("languages", ["en-US"])[0],
            timezone_id="America/New_York"
        )
        
        await self.context.add_init_script(f"""
            Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
            Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {self.profile.get('hardware_concurrency', 8)} }});
            Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {self.profile.get('device_memory', 8)} }});
            Object.defineProperty(navigator, 'platform', {{ get: () => '{self.profile.get('platform', 'Win32')}' }});
        """)

    async def shutdown(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
