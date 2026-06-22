import json
from pathlib import Path
from utils.log_rotator import get_logger

log = get_logger("SessionInjector")

class SessionInjector:
    """Handles injection of session identifiers into active browser contexts."""
    def __init__(self, cookie_file="/home/tangleroot013/god_stack/secrets/session_cookies.json"):
        self.cookie_file = Path(cookie_file)

    def load_cookies(self) -> list:
        """Retrieves verified authorization sequences from disk."""
        if not self.cookie_file.exists():
            log.warning(f"No authentication parameters located at: {self.cookie_file}")
            return []
        try:
            with open(self.cookie_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Error reading authentication file parameters: {e}")
            return []

    def inject_into_playwright(self, target_domain: str, playwright_context):
        """Applies pre-cached authorization states to active contexts."""
        cookies = self.load_cookies()
        if not cookies:
            log.warning("Skipping cookie injection: configuration structure is empty.")
            return False
            
        try:
            playwright_context.add_cookies(cookies)
            log.info(f"✅ Injected {len(cookies)} tracking cookies into browser domain: {target_domain}")
            return True
        except Exception as e:
            log.error(f"Authentication injection error vector: {e}")
            return False
