import asyncio
import logging
from typing import List, Dict, Any
from markdownify import markdownify as md
from playwright.async_api import async_playwright
from utils.captcha_handler import CaptchaHandler
from utils.stealth_manager import StealthManager

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[GOD-ENGINE]\033[0m %(message)s")
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.sentinel = CaptchaHandler()
        self.identity_handler = StealthManager()

    async def initialize(self, headless: bool = True, persistent_id: str = None):
        """Initializes browser contexts with dynamic persistence parameters."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        
        identity = self.identity_handler.dispatch_identity(persistent_id=persistent_id)
        logger.info(f"Injecting stealth identity payload UA: {identity['user_agent']}")
        
        self.context = await self.browser.new_context(user_agent=identity["user_agent"])
        await self.context.add_cookies(identity["cookies"])

    async def scrape(self, url: str, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        page = await self.context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded")
            for step in workflow:
                if step.get("action") == "scroll":
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)

            content = await page.content()
            threat = self.sentinel.inspect_page_source(content)
            if threat != "clean":
                token = await self.sentinel.deploy_solver_bridge(threat, url)
                await page.evaluate(f"() => {{ if (typeof window.finishCaptcha === 'function') {{ window.finishCaptcha('{token}'); }} }}")
            
            title = await page.title()
            return {"status": "success", "title": title, "markdown": md(content)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
