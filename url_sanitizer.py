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
    """Enforces strict structural compliance with modern browser network layers."""
    
    @staticmethod
    def normalize(raw_url: str, strip_trackers: bool = True) -> str:
        """Transforms erratic web strings into normalized, web-compliant endpoints."""
        if not raw_url or not isinstance(raw_url, str):
            return ""

        cleaned = raw_url.strip()
        
        # Enforce scheme baseline if dropped by mistake
        if cleaned.startswith("//"):
            cleaned = "https:" + cleaned
        elif not cleaned.startswith(("http://", "https://")):
            cleaned = "https://" + cleaned

        try:
            parsed = urlparse(cleaned)
            
            # Extract and filter query string parameters
            query_params = parse_qsl(parsed.query)
            
            if strip_trackers:
                # Discard common behavioral analytics tracking noise
                blacklisted_keys = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid", "fbclid"}
                query_params = [(k, v) for k, v in query_params if k.lower() not in blacklisted_keys]

            # Re-serialize components back to spec alignment
            normalized_query = urlencode(query_params)
            normalized_path = parsed.path if parsed.path else "/"
            
            final_url = urlunparse((
                parsed.scheme.lower(),      # Schemes are lowercase per WHATWG spec
                parsed.netloc.lower(),      # Hostnames must evaluate to lowercase
                normalized_path,
                parsed.params,
                normalized_query,
                ""                          # Strip fragment identifiers (hash anchors aren't sent to servers)
            ))
            
            if final_url != raw_url:
                logger.info(f"Normalized link mutation: {raw_url} -> \033[1;36m{final_url}\033[0m")
            return final_url

        except Exception as e:
            logger.error(f"WHATWG specification violation parsing input structural link: {str(e)}")
            return cleaned

if __name__ == "__main__":
    print("\n\033[1;35m--- EVALUATING STRUCTURAL URL COMPLIANCE ENGINE ---\033[0m")
    
    dirty_urls = [
        "NEWS.YCOMBINATOR.COM/newest/",
        "https://news.ycombinator.com/front?utm_source=twitter&utm_medium=social&id=123#comments",
        "//news.ycombinator.com/ask?search=python++programming"
    ]
    
    for url in dirty_urls:
        UrlSanitizer.normalize(url)
