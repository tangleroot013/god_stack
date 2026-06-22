import asyncio
import json
import logging
import yaml
import os
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright, Page

# Import the standalone CaptchaHandler component
from utils.captcha_handler import CaptchaHandler

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[GOD-SCRAPER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self, profile_path: str = "stealth_profiles.yaml", profile_name: str = "high_privacy_profile"):
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
            logger.warning("Profile config missing or unreadable. Falling back to internal engine safety defaults.")
            return {
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
                "viewport": {"width": 1440, "height": 900}
            }

    async def initialize(self, headless: bool = True):
        """Spawns the isolated browser layer using custom stealth profiles."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        
        self.context = await self.browser.new_context(
            user_agent=self.profile.get("user_agent"),
            viewport=self.profile.get("viewport"),
            locale=self.profile.get("languages", ["en-US"])[0]
        )
        logger.info("Playwright browser instance and stealth context mounted successfully.")

    async def evaluate_perimeter(self, page: Page, url: str) -> bool:
        """Inspects live DOM state for interstitial verification screens or script blocks."""
        html_content = await page.content()
        threat = self.sentinel.inspect_page_source(html_content)
        
        if threat != "clean":
            logger.warning(f"Perimeter mitigation triggered for stateful target: {threat.upper()}")
            # Route state parameters to solver bridge
            resolved = self.sentinel.deploy_solver_bridge(threat, url)
            if not resolved:
                logger.error("Stateful interceptor failed to clear the perimeter challenge frame.")
                return False
            # Allow DOM time to settle post-token verification
            await page.wait_for_timeout(3000)
        return True

    async def execute_workflow(self, page: Page, workflow: List[Dict[str, Any]]):
        """Processes complex behavioral matrices sequentially."""
        for step in workflow:
            action = step.get("action")
            target = step.get("target")
            value = step.get("value")

            logger.info(f"Executing workflow transaction step: Action={action} Target={target}")

            if action == "type" and target and value:
                await page.fill(target, value)
            elif action == "click" and target:
                await page.click(target)
            elif action == "wait_for" and target:
                await page.wait_for_selector(target, timeout=5000)
            elif action == "scroll":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
            
            # Post-action security monitoring
            perimeter_clear = await self.evaluate_perimeter(page, page.url)
            if not perimeter_clear:
                raise RuntimeError("Workflow halted by unnegotiated anti-bot framework.")

    async def scrape(self, url: str, workflow: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Navigates to an endpoint, executes automation matrices, and serializes clean markdown."""
        if not self.context:
            raise RuntimeError("Scraper profile layer not initialized. Run initialize() first.")

        page = await self.context.new_page()
        try:
            logger.info(f"Navigating browser stream directly to target node: {url}")
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Perform initial triage inspection
            if not await self.evaluate_perimeter(page, url):
                return {"status": "blocked", "message": "Initial access restricted by target perimeter."}

            # If an interactive matrix is provided, process it step-by-step
            if workflow:
                await self.execute_workflow(page, workflow)

            # Final data parsing and structural translation
            html_content = await page.content()
            soup = BeautifulSoup(html_content, "html.parser")
            page_title = soup.title.string if soup.title else "Untitled Target Node"
            markdown_content = md(html_content)

            return {
                "status": "success",
                "title": page_title,
                "url": page.url,
                "markdown": markdown_content
            }
        except Exception as e:
            logger.error(f"Stateful automation processing failure: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()
        logger.info("Stateful browser engines powered down cleanly.")

if __name__ == "__main__":
    async def test_run():
        print("\n\033[1;35m--- INITIALIZING INTEGRATED PLAYWRIGHT SENTINEL SANDBOX ---\033[0m")
        
        # Verify directory structures exist prior to simulation execution
        os.makedirs("vaults", exist_ok=True)
        
        scraper = GodScraper()
        await scraper.initialize(headless=True)
        
        # Simulating interaction on an open portal layout
        target = "https://quotes.toscrape.com/login"
        mock_flow = [
            {"action": "type", "target": "input[name='username']", "value": "tangleroot013"},
            {"action": "type", "target": "input[name='password']", "value": "orchestration_matrix_99"},
            {"action": "click", "target": "input[type='submit']"},
            {"action": "scroll"}
        ]
        
        result = await scraper.scrape(url=target, workflow=mock_flow)
        await scraper.shutdown()
        
        print(f"\n\033[1;32m[SANDBOX RESULT STATUS]\033[0m: {result.get('status').upper()}")
        if result.get("status") == "success":
            print(f"Extracted Node Title: {result.get('title')}")
            print(f"Payload Preview:\n{result.get('markdown')[:200].strip()}\n...")

    asyncio.run(test_run())
