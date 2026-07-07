# ==============================================================================
# BROWSER INTEL AUTOMATION CORE (god_scraper.py)
# Architecture: Playwright Sandbox with Modular Action Chains & Error Resilience
# ==============================================================================
import asyncio
import json
import logging
import yaml
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright, Page

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[GOD-ENGINE]\033[0m %(message)s"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, profile_path: str = "stealth_profiles.yaml", profile_name: str = "default_profile"):
        self.profile = self._load_profile(profile_path, profile_name)
        self.playwright = None
        self.browser = None
        self.context = None

    def _load_profile(self, path: str, name: str) -> Dict[str, Any]:
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)
                return config.get(name, config.get("default_profile"))
        except Exception:
            logger.warning("Profile config missing. Falling back to internal engine safety defaults.")
            return {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    async def initialize(self, headless: bool = True, proxy_url: Optional[str] = None):
        self.playwright = await async_playwright().start()
        
        launch_args = []
        proxy_config = None
        
        if proxy_url:
            proxy_config = {"server": proxy_url}
            
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=launch_args,
            proxy=proxy_config
        )
        
        self.context = await self.browser.new_context(
            user_agent=self.profile.get("user_agent"),
            viewport=self.profile.get("viewport"),
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )

    async def scrape(self, url: str, workflow: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if not self.context:
            return {"status": "error", "message": "Engine context uninitialized."}

        page = await self.context.new_page()
        try:
            # Main navigation threshold
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Action array pipeline tracking
            if workflow:
                for step in workflow:
                    action = step.get("action")
                    target = step.get("target")
                    val = step.get("value")
                    
                    logger.info(f"Executing workflow step: [Action: {action}] -> [Target: {target or 'N/A'}]")
                    
                    if action == "click" and target:
                        await page.click(target, timeout=5000)
                    elif action == "type" and target and val:
                        await page.type(target, val, timeout=5000)
                    elif action == "wait_for" and target:
                        await page.wait_for_selector(target, timeout=5000)
                    elif action == "scroll":
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                    elif action == "wait_for_timeout":
                        await page.wait_for_timeout(int(val or 1000))

            raw_html = await page.content()
            title = await page.title()
            markdown_content = md(raw_html)
            
            return {
                "status": "success",
                "title": title,
                "html": raw_html,
                "markdown": markdown_content
            }
        except Exception as e:
            logger.error(f"Scraping execution crashed: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            try:
                await page.close()
            except Exception:
                pass

    async def shutdown(self):
        """Resilient process closure designed to swallow OS driver interrupts silently."""
        try:
            if self.browser: 
                await self.browser.close()
        except Exception:
            pass
        finally:
            try:
                if self.playwright: 
                    await self.playwright.stop()
            except Exception:
                pass

if __name__ == "__main__":
    async def run_test():
        scraper = GodScraper()
        await scraper.initialize(headless=True)
        res = await scraper.scrape("https://news.ycombinator.com")
        print(f"Scraping complete status: {res.get('status')}")
        await scraper.shutdown()
    asyncio.run(run_test())
