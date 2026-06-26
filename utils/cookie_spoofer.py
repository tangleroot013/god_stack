import secrets
import string
import json
import os

class CookieSpoofer:
    """Manages both randomized session masks and persistent credential states."""
    def __init__(self, session_dir="/home/tangleroot013/god_stack/outputs/sessions"):
        self.common_keys = ["session_id", "csrftoken", "_ga", "_gid", "auth_token"]
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def generate_spoofed_jar(self) -> dict:
        """Generates a randomized cookie dictionary for unauthenticated requests."""
        jar = {}
        for _ in range(secrets.randbelow(4) + 3):
            key = secrets.choice(self.common_keys) + "_" + self._rand_str(4)
            val = self._rand_str(32)
            jar[key] = val
        return jar

    def save_session(self, identity: str, cookie_jar: dict):
        """Persists a specific credential state to disk for future mission cycles."""
        path = os.path.join(self.session_dir, f"{identity}.json")
        with open(path, "w") as f:
            json.dump(cookie_jar, f)

    def load_session(self, identity: str) -> dict:
        """Retrieves a persistent session identity to maintain deep state handling."""
        path = os.path.join(self.session_dir, f"{identity}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return self.generate_spoofed_jar()

    def format_for_playwright(self, cookie_dict: dict, domain: str = ".toscrape.com") -> list:
        """Translates flat key-value session maps into structured Playwright storage cookies."""
        import time
        return [
            {
                "name": k,
                "value": v,
                "domain": domain,
                "path": "/",
                "expires": time.time() + 3600,
                "httpOnly": False,
                "secure": False,
                "sameSite": "Lax"
            }
            for k, v in cookie_dict.items()
        ]

    def _rand_str(self, length: int) -> str:
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))
