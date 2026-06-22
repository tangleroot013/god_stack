import asyncio
import json
import os
import logging
import yaml
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright
from utils.captcha_handler import CaptchaHandler

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[GOD-ENGINE]\033[0m %(message)s"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, profile_path: str = "/home/tangleroot013/god_stack/stealth_profiles.yaml", profile_name: str = "default_profile"):
        self.profile = self._load_profile(profile_path, profile_name)
        self.playwright = None
        self.browser = None
        self.context = None
        self.sentinel = CaptchaHandler()

    def _load_profile(self, path: str, name: str) -> Dict[str, Any]:
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)
                return config.get(name, config.get("default_profile"))
        except Exception:
            logger.warning("Profile config missing. Falling back to internal engine safety defaults.")
            return {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async def initialize(self, headless: bool = True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.context = await self.browser.new_context(
            user_agent=self.profile.get("user_agent"),
            viewport=self.profile.get("viewport"),
            screen=self.profile.get("screen"),
            locale=self.profile.get("languages", ["en-US"])[0]
        )

    async def scrape(self, url: str, workflow: List[Dict[str, Any]]) -> Dict[str, Any]:
        page = await self.context.new_page()
        try:
            logger.info(f"Navigating stateful session target: {url}")
            await page.goto(url, wait_until="domcontentloaded")
            
            for step in workflow:
                action = step.get("action")
                target = step.get("target")
                value = step.get("value", "")
                
                if action == "type":
                    logger.info(f"Interacting with dynamic DOM: typing into '{target}'")
                    await page.fill(target, value)
                elif action == "click":
                    logger.info(f"Dispatching UI pointer click event: '{target}'")
                    await page.click(target)
                elif action == "scroll":
                    logger.info("Executing fluid scroll matrix adjustments...")
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(1)

            # --- POST NAVIGATION SENTINEL CHECK ---
            content = await page.content()
            threat = self.sentinel.inspect_page_source(content)
            
            if threat != "clean":
                token = await self.sentinel.deploy_solver_bridge(threat, url)
                await page.evaluate(f"() => {{ if (typeof window.finishCaptcha === 'function') {{ window.finishCaptcha('{token}'); }} }}")
            
            title = await page.title()
            markdown_content = md(content)
            
            return {
                "status": "success",
                "title": title,
                "markdown": markdown_content
            }
        except Exception as e:
            logger.error(f"Scraping execution crashed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
        logger.info("Stateful browser engines powered down cleanly.")
