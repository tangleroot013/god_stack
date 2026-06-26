# ==============================================================================
# G.O.D. SCRAPER CORE (god_scraper.py)
# Architecture: Unified orchestration of routing, sanitization, and evasion.
# ==============================================================================

import logging
from utils.courlan_router import CourlanRouter
from utils.url_sanitizer import UrlSanitizer
from utils.captcha_handler import CaptchaHandler

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;35m[GOD-SCRAPER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("GodScraper")

class GodScraper:
    def __init__(self):
        self.router = CourlanRouter()
        self.sanitizer = UrlSanitizer()
        self.sentinel = CaptchaHandler()

    def process_target(self, raw_url: str, mock_html: str = "") -> bool:
        """Runs a target URL through the complete defensive pipeline."""
        logger.info(f"🚀 Initializing ingestion sequence for: {raw_url}")
        
        # Step 1: WHATWG Normalization
        sanitized_url = self.sanitizer.normalize(raw_url)
        if not sanitized_url:
            logger.error("Pipeline aborted: Failed WHATWG sanitization.")
            return False

        # Step 2: Frontier Validation
        safe_url = self.router.validate_and_clean(sanitized_url)
        if not safe_url:
            logger.error("Pipeline aborted: Target failed frontier validation (possible crawler trap).")
            return False

        # Step 3: Anti-Bot Sentinel Check
        logger.info(f"Target locked and routed: {safe_url}. Inspecting payload...")
        threat = self.sentinel.inspect_page_source(mock_html)
        
        if threat != "clean":
            resolved = self.sentinel.deploy_solver_bridge(threat, safe_url)
            if not resolved:
                logger.error("Pipeline aborted: Failed to negotiate perimeter defense.")
                return False

        logger.info("✅ Ingestion complete. Payload secure and verified.")
        return True

if __name__ == "__main__":
    print("\n\033[1;36m==================================================\033[0m")
    print("\033[1;36m    INITIATING G.O.D. CORE PIPELINE DIAGNOSTIC    \033[0m")
    print("\033[1;36m==================================================\033[0m")
    
    scraper = GodScraper()
    
    dirty_target = "HTTPS://NEWS.YCOMBINATOR.COM/item?id=300&utm_source=test#comments"
    mock_cloudflare_html = "<html><script src='https://challenges.cloudflare.com/turnstile/v0/api.js'></script></html>"
    
    scraper.process_target(dirty_target, mock_cloudflare_html)
