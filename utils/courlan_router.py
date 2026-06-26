# ==============================================================================
# ADVANCED FRONTIER URL ROUTER (courlan_router.py)
# Architecture: High-Performance Normalization and Crawler Trap Avoidance
# ==============================================================================

import logging
import courlan
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;33m[COURLAN-ROUTER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CourlanRouter")

class CourlanRouter:
    """Handles URL normalization, cleanliness checks, and tracking parameter removal."""

    @staticmethod
    def validate_and_clean(url: str) -> str:
        """
        Validates, scrubs tracking parameters, and checks against crawl traps.
        Returns a pristine URL string, or an empty string if malicious/invalid.
        """
        if not url or not isinstance(url, str):
            return ""

        logger.info(f"Passing target through Courlan frontier filters: {url}")
        
        try:
            # 1. Clean tracking fragments and normalize structural components
            cleaned_url = courlan.clean_url(url)
            if not cleaned_url:
                return ""

            # 2. Validate structural integrity using core Courlan validation parser
            validation_check = courlan.validate_url(cleaned_url)
            if not validation_check:
                logger.warning(f"URL rejected by Courlan validation filters: {url}")
                return ""

            # 3. Defensive heuristic check against deep recursion / crawler loop paths
            parsed_obj = urlparse(cleaned_url)
            path_segments = [seg for seg in parsed_obj.path.split('/') if seg]
            if len(path_segments) > 5 and len(set(path_segments)) < (len(path_segments) / 2):
                logger.warning(f"Dropping suspected recursive loop path pattern: {cleaned_url}")
                return ""

            return cleaned_url

        except Exception as parse_error:
            logger.error(f"Non-critical anomaly encountered filtering {url}: {str(parse_error)}")
            return ""

if __name__ == "__main__":
    test_target = "https://news.ycombinator.com/item?id=123&utm_source=feed#hash"
    result = CourlanRouter.validate_and_clean(test_target)
    print(f"\nScrubbed Output: {result}")
