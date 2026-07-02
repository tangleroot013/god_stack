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
    @staticmethod
    def validate_and_clean(url: str) -> str:
        if not url or not isinstance(url, str):
            return ""
        try:
            cleaned_url = courlan.clean_url(url)
            if not cleaned_url or not courlan.validate_url(cleaned_url):
                return ""
            parsed_obj = urlparse(cleaned_url)
            path_segments = [seg for seg in parsed_obj.path.split('/') if seg]
            if len(path_segments) > 5 and len(set(path_segments)) < (len(path_segments) / 2):
                return ""
            return cleaned_url
        except Exception:
            return ""
