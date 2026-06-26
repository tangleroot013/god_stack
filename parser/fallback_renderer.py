#!/usr/bin/env python3
import sys
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def render(url: str, out_path: str):
    # Intercept and mask the browser context at the generation layer
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Short-circuit long analytical tracking frames using domcontentloaded
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            
            # Settle period for asynchronous client-side JS hydration
            await page.wait_for_timeout(3000)
            
            content = await page.content()
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            print(f"[RENDER ERROR] Failed processing execution path for {url}: {str(e)}", file=sys.stderr)
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: fallback_renderer.py <url> <output_html>")
        sys.exit(1)
    asyncio.run(render(sys.argv[1], sys.argv[2]))
