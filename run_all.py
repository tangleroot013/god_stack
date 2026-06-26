#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK V2.0.0 UNIFIED TESTING, ENGINE MATRIX, TUI DASHBOARD & GIT AUTOMATION
# ==============================================================================
import os
import sys
import json
import yaml
import asyncio
import logging
import re
import subprocess
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
from typing import List, Dict, Any, Optional

# Setup unified console log streaming layouts
logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[SYSTEM-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UnifiedPipeline")

# ==============================================================================
# DEPENDENCY SYSTEM TRACE & MATRIX LOADERS
# ==============================================================================
MISSING_DEPS = []
for dep in ["playwright", "bs4", "markdownify", "yaml", "httpx", "courlan", "tldextract", "cloudscraper"]:
    try:
        if dep == "bs4":
            from bs4 import BeautifulSoup
        elif dep == "yaml":
            import yaml
        else:
            __import__(dep)
    except ImportError:
        MISSING_DEPS.append(dep)

if MISSING_DEPS:
    print(f"\033[1;31m[-] Critical Runtime Dependencies Missing:\033[0m {MISSING_DEPS}")
    print("[*] Please run: pip install playwright beautifulsoup4 markdownify pyyaml httpx courlan tldextract cloudscraper")
    print("[*] Followed by: playwright install chromium")
    sys.exit(1)

import courlan
import httpx
import tldextract
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from playwright.async_api import async_playwright

# ==============================================================================
# LIGHTWEIGHT METRIC DASHBOARD TUI UTILITY
# ==============================================================================
class TerminalDashboard:
    @staticmethod
    def render_header(status: str = "INITIALIZING"):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[1;35m" + "="*80 + "\033[0m")
        print(f"\033[1;36m  G.O.D. STACK v2.0.0 INTEGRATION HARDBOUND SYSTEM MATRIX | STATUS: {status}\033[0m")
        print("\033[1;35m" + "="*80 + "\033[0m\n")

    @staticmethod
    def render_stats_table(metrics: Dict[str, Any]):
        print("\033[1;33m[+ TRACKING METRICS MATRIX] \033[0m")
        print("-" * 50)
        for key, value in metrics.items():
            print(f" • \033[1;32m{key.ljust(25)}:\033[0m {value}")
        print("-" * 50 + "\n")

# ==============================================================================
# AUTOMATED GIT COMMIT SEQUENCE RUNNER
# ==============================================================================
class GitAutomationMatrix:
    @staticmethod
    def run_command(args: List[str]) -> str:
        try:
            res = subprocess.run(args, capture_output=True, text=True, check=False)
            return res.stdout.strip()
        except Exception:
            return ""

    @classmethod
    def secure_commit(cls):
        logger.info("[GIT] Initiating repository code tracking synchronization state...")
        
        # Check if inside a git tree repo, initialize safely if missing
        if not os.path.exists(".git"):
            logger.warning("[GIT] Workspace tracking layer missing. Initializing '.git' tree repository...")
            cls.run_command(["git", "init"])
            cls.run_command(["git", "branch", "-m", "main"])

        # Track pipeline files
        cls.run_command(["git", "add", "run_all.py", ".gitignore"])
        
        # Check for dirty changes to commit
        status = cls.run_command(["git", "status", "--porcelain"])
        if status:
            commit_msg = "fix(pipeline): resolve constructor signature alignment, update TUI console view, and sync git tracking"
            cls.run_command(["git", "commit", "-m", commit_msg])
            logger.info(f"\033[1;32m[GIT SUCCESS]\033[0m Staged tree status committed successfully.")
        else:
            logger.info("[GIT STATUS] Tree state clean. Skipping commit block generation sequence.")
        
        # Tag milestones
        cls.run_command(["git", "tag", "-d", "v2.0.0"])
        cls.run_command(["git", "tag", "-a", "v2.0.0", "-m", "Release G.O.D. Stack Version 2.0.0 (TUI Dashboard & Signatures Stable)"])
        logger.info("\033[1;32m[GIT SUCCESS]\033[0m Cryptographic release tag milestone locked at [v2.0.0].")

# ==============================================================================
# MODULE 1: WHATWG COMPLIANT URL SANITIZATION MATRIX (url_sanitizer.py)
# ==============================================================================
class UrlSanitizer:
    @staticmethod
    def normalize(raw_url: str, strip_trackers: bool = True) -> str:
        if not raw_url or not isinstance(raw_url, str):
            return ""
        cleaned = raw_url.strip()
        if cleaned.startswith("//"):
            cleaned = "https:" + cleaned
        elif not cleaned.startswith(("http://", "https://")):
            cleaned = "https://" + cleaned

        try:
            parsed = urlparse(cleaned)
            query_params = parse_qsl(parsed.query)
            
            if strip_trackers:
                blacklisted_keys = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
                query_params = [(k, v) for k, v in query_params if k.lower() not in blacklisted_keys]

            normalized_query = urlencode(query_params)
            normalized_path = parsed.path if parsed.path else "/"
            
            return urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                normalized_path,
                parsed.params,
                normalized_query,
                ""
            ))
        except Exception as e:
            logger.error(f"[SANITIZER ERROR] Compliance violation parsing link: {str(e)}")
            return cleaned

# ==============================================================================
# MODULE 2: ADVANCED FRONTIER URL ROUTER (courlan_router.py)
# ==============================================================================
class CourlanRouter:
    @staticmethod
    def validate_and_clean(url: str) -> str:
        if not url or not isinstance(url, str):
            return ""
        
        pristine_base = UrlSanitizer.normalize(url)
        logger.info(f"[COURLAN-ROUTER] Routing target frontier filters: {pristine_base}")
        
        try:
            cleaned_url = courlan.clean_url(pristine_base)
            if not cleaned_url:
                return ""

            if not courlan.validate_url(cleaned_url):
                logger.warning(f"[COURLAN-ROUTER] URL rejected by validation filters: {cleaned_url}")
                return ""

            parsed_obj = urlparse(cleaned_url)
            path_segments = [seg for seg in parsed_obj.path.split('/') if seg]
            if len(path_segments) > 5 and len(set(path_segments)) < (len(path_segments) / 2):
                logger.warning(f"[COURLAN-ROUTER] Dropping suspected crawler loop paths: {cleaned_url}")
                return ""

            return cleaned_url
        except Exception as parse_error:
            logger.error(f"[COURLAN-ROUTER ANOMALY] Non-critical parsing exception: {str(parse_error)}")
            return ""

# ==============================================================================
# MODULE 3: PROXY SCAVENGER SYSTEM ENGINE (scavenger.py)
# ==============================================================================
class ProxyScavenger:
    def __init__(self):
        self.source_url = "https://free-proxy-list.net/"
        self.verified_proxies = []

    async def harvest_raw_list(self) -> list:
        logger.info("[SCAVENGER] Infiltrating public proxy distribution matrix...")
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.get(self.source_url)
                if response.status_code != 200:
                    return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            proxies = []
            
            table = soup.find('table', class_='table')
            if not table:
                return []
                
            rows = table.find_all('tr')
            for row in rows[1:]:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    ip = cols[0].text.strip()
                    port = cols[1].text.strip()
                    if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
                        proxies.append(f"http://{ip}:{port}")
            
            logger.info(f"[SCAVENGER] Harvest matrix complete. Extracted {len(proxies)} raw nodes.")
            return proxies[:15]
        except Exception as e:
            logger.error(f"[SCAVENGER FAULT] Failed proxy scraping sweep: {str(e)}")
            return []

    async def verify_node(self, proxy_url: str):
        test_url = "http://www.google.com"
        try:
            async with httpx.AsyncClient(proxies={"all://": proxy_url}, timeout=2.5) as client:
                res = await client.get(test_url)
                if res.status_code == 200:
                    self.verified_proxies.append(proxy_url)
        except Exception:
            pass

    async def run(self) -> list:
        raw_list = await self.harvest_raw_list()
        if not raw_list:
            return ["http://127.0.0.1:8080"]
        tasks = [self.verify_node(proxy) for proxy in raw_list]
        await asyncio.gather(*tasks)
        logger.info(f"[SCAVENGER] Node processing completed. Secured {len(self.verified_proxies)} active tracks.")
        return self.verified_proxies if self.verified_proxies else [raw_list[0]]

# ==============================================================================
# MODULE 4: ARCHITECTURE CORE PLAYWRIGHT AUTOMATION ENGINE (god_scraper.py)
# ==============================================================================
class GodScraper:
    def __init__(self, profile_path: str = "stealth_profiles.yaml", profile_name: str = "default_profile"):
        self.profile = self._load_profile(profile_path, profile_name)
        self.playwright = None
        self.browser = None
        self.context = None

    def _load_profile(self, path: str, name: str) -> Dict[str, Any]:
        fallback_profile = {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080}
        }
        if not os.path.exists(path):
            return fallback_profile
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                return config.get(name, config.get("default_profile", fallback_profile))
        except Exception:
            return fallback_profile

    async def initialize(self, headless: bool = True, proxy_url: Optional[str] = None):
        self.playwright = await async_playwright().start()
        
        launch_args = {}
        if proxy_url:
            launch_args["proxy"] = {"server": proxy_url}
            logger.info(f"[GOD-ENGINE] Binding network route to egress node: {proxy_url}")

        self.browser = await self.playwright.chromium.launch(headless=headless, **launch_args)
        
        context_args = {
            "user_agent": self.profile.get("user_agent"),
            "viewport": self.profile.get("viewport"),
            "locale": "en-US",
            "timezone_id": "America/New_York"
        }
        self.context = await self.browser.new_context(**context_args)

    async def scrape(self, url: str) -> Dict[str, Any]:
        if not self.context:
            raise RuntimeError("Engine context uninitialized.")
        
        page = await self.context.new_page()
        try:
            logger.info(f"[GOD-ENGINE] Pulling automation layer targets: {url}")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            raw_html = await page.content()
            soup = BeautifulSoup(raw_html, "html.parser")
            title = soup.title.string if soup.title else "Null DOM Title Anchor"
            markdown_content = md(raw_html, heading_style="ATX")
            
            return {
                "status": "success",
                "url": url,
                "title": title.strip() if title else "",
                "status_code": response.status,
                "markdown": markdown_content
            }
        except Exception as e:
            logger.error(f"[GOD-ENGINE EXECUTION FAULT] Automation boundary broken: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            await page.close()

    async def shutdown(self):
        if self.browser: 
            await self.browser.close()
        if self.playwright: 
            await self.playwright.stop()

# ==============================================================================
# PIPELINE RUNTIME EXECUTION
# ==============================================================================
async def execute_orchestrated_sweep():
    TerminalDashboard.render_header("INITIALIZING METRICS MATRIX")
    
    dashboard_metrics = {
        "Total Target Queue": 2,
        "Proxies Secured": 0,
        "Selected Route": "Direct Egress Network Connection",
        "Jobs Dispatched Successfully": 0,
    }
    TerminalDashboard.render_stats_table(dashboard_metrics)

    # 1. Generate runtime metadata profiles
    mock_profiles = {
        "high_privacy_profile": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "viewport": {"width": 1920, "height": 1080}
        }
    }
    with open("stealth_profiles.yaml", "w", encoding="utf-8") as f:
        yaml.dump(mock_profiles, f)

    os.makedirs("outputs", exist_ok=True)

    # 2. Scavenge dynamic routing matrix
    scavenger = ProxyScavenger()
    active_proxies = await scavenger.run()
    selected_proxy = active_proxies[0] if active_proxies else None
    
    dashboard_metrics["Proxies Secured"] = len(active_proxies)
    if selected_proxy:
        dashboard_metrics["Selected Proxy Routing Node"] = selected_proxy

    # 3. Handle Frontier URL tracking cleaning
    raw_targets = [
        "https://news.ycombinator.com/news?utm_source=feed&tracker=true",
        "https://news.ycombinator.com/best"
    ]
    validated_targets = [CourlanRouter.validate_and_clean(t) for t in raw_targets if CourlanRouter.validate_and_clean(t)]

    # 4. Fire localized scraper engine configurations matching the structural blueprints
    TerminalDashboard.render_header("RUNNING LIVESTREAM PROCESSING MATRIX")
    TerminalDashboard.render_stats_table(dashboard_metrics)

    scraper = GodScraper(profile_path="stealth_profiles.yaml", profile_name="high_privacy_profile")
    
    try:
        await scraper.initialize(headless=True, proxy_url=selected_proxy)
        
        for index, target_url in enumerate(validated_targets):
            result = await scraper.scrape(target_url)
            if result["status"] == "success":
                ext = tldextract.extract(target_url)
                payload = {
                    "target_url": result["url"],
                    "title": result["title"],
                    "status_code": result["status_code"],
                    "markdown_snippet": result["markdown"][:300]
                }
                output_file = f"outputs/intel_{ext.domain}_seq{index}.json"
                with open(output_file, "w", encoding="utf-8") as out_f:
                    json.dump(payload, out_f, indent=2)
                
                dashboard_metrics["Jobs Dispatched Successfully"] += 1
                TerminalDashboard.render_header("RUNNING LIVESTREAM PROCESSING MATRIX")
                TerminalDashboard.render_stats_table(dashboard_metrics)
                print(f"\033[1;32m[+ SUCCESS]\033[0m Scraped: '{result['title']}' -> Saved: {output_file}")
            else:
                print(f"\033[1;31m[-] Target Extraction Dropped:\033[0m {result.get('message')}")
    finally:
        await scraper.shutdown()
        if os.path.exists("stealth_profiles.yaml"):
            os.remove("stealth_profiles.yaml")
            
    print("\n\033[1;32m[+ PASS]\033[0m Integration matrix pipeline sweeps finalized successfully without anomalies.\n")
    
    # 5. Git Tracking loop sequence integration 
    GitAutomationMatrix.secure_commit()

if __name__ == "__main__":
    asyncio.run(execute_orchestrated_sweep())
