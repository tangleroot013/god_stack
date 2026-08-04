# ==============================================================================
# WHATWG COMPLIANT URL SANITIZATION MATRIX (url_sanitizer.py)
# Architecture: Standardized Normalization & Query Parameter Stripping
# ==============================================================================
import logging
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[SANITIZER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UrlSanitizer")

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
                blacklisted_keys = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "click_id", "fbclid"}
                query_params = [(k, v) for k, v in query_params if k.lower() not in blacklisted_keys]

            normalized_query = urlencode(query_params)
            normalized_path = parsed.path if parsed.path else "/"
            final_url = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                normalized_path,
                parsed.params,
                normalized_query,
                ""
            ))
            if final_url != raw_url:
                logger.info(f"Normalized link mutation: {raw_url} -> \033[1;36m{final_url}\033[0m")
            return final_url
        except Exception as e:
            logger.error(f"WHATWG specification violation parsing input structural link: {str(e)}")
            return cleaned
