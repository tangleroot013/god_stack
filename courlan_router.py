#!/usr/bin/env python3
import logging
import courlan
from urllib.parse import urlparse
from url_sanitizer import UrlSanitizer

logger = logging.getLogger("CourlanRouter")
logging.basicConfig(level=logging.INFO)

class CourlanRouter:
    """Handles URL normalization, cleanliness checks, and tracking parameter removal."""

    @staticmethod
    def validate_and_clean(url: str) -> str:
        if not url or not isinstance(url, str):
            return ""

        # 1️⃣ Apply static normalizer first to fix case and standard tracking tokens
        url = UrlSanitizer.normalize(url)
        logger.info(f"Passing target through Courlan frontier filters: {url}")

        try:
            # 2️⃣ Execute deep path-cleansing via Courlan engine
            cleaned_url = courlan.clean_url(url)
            if not cleaned_url:
                return ""

            # 3️⃣ Explicitly strip trailing browser hash/fragments 
            cleaned_url = cleaned_url.split('#', 1)[0]

            # 4️⃣ Validate runtime structural safety
            if not courlan.validate_url(cleaned_url):
                logger.warning(f"URL rejected by Courlan validation filters: {url}")
                return ""

            # 5️⃣ Isolate recursive traversal traps
            path_segments = [seg for seg in urlparse(cleaned_url).path.split('/') if seg]
            if len(path_segments) > 5 and len(set(path_segments)) < len(path_segments) / 2:
                logger.warning(f"Dropping suspected recursive loop path pattern: {cleaned_url}")
                return ""

            return cleaned_url

        except Exception as parse_error:
            logger.error(f"Non-critical anomaly encountered filtering {url}: {str(parse_error)}")
            return ""

if __name__ == "__main__":
    test_target = "HTTPS://NEWS.YCOMBINATOR.COM/item?id=1&utm_source=twitter#hash"
    result = CourlanRouter.validate_and_clean(test_target)
    print(f"Router Dry-Run Verification: {result}")
