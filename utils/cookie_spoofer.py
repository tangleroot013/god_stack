import time
import secrets

class CookieSpoofer:
    """Generates a dynamic, warmed-up mock cookie jar signature to emulate organic use."""
    def generate_spoofed_jar(self) -> list:
        return [
            {
                "name": "session_id",
                "value": secrets.token_hex(16),
                "domain": ".example.com",
                "path": "/",
                "expires": time.time() + 3600,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax"
            }
        ]
