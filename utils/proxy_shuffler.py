import json
import logging
import random
from pathlib import Path
from typing import Dict, List

log = logging.getLogger("ProxyShuffler")

class ProxyRotationPool:
    """Manages an active array of proxy targets loaded from config specifications."""
    
    def __init__(self, proxy_config_path="/home/tangleroot013/god_stack/config/proxies.json"):
        self.config_path = Path(proxy_config_path)
        self.proxies = self._load_pool()

    def _load_pool(self) -> List[Dict[str, any]]:
        try:
            if not self.config_path.exists():
                return []
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
            return data.get("proxies", [])
        except Exception as e:
            log.error(f"Failed to parse proxy pool configurations: {e}")
            return []

    def get_isolated_proxy(self) -> Dict[str, any]:
        """Returns a single random proxy configuration profile from the pool."""
        if not self.proxies:
            return {"host": None, "port": None, "username": None, "password": None}
        return random.choice(self.proxies)


class FingerprintShuffler:
    """Generates realistic client hardware properties to decouple session nodes."""

    FINGERPRINT_PROFILES = [
        {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "vendor": "Intel Inc.", "renderer": "Intel Iris Xe Graphics"},
        {"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15", "vendor": "Apple Inc.", "renderer": "Apple M2 Engine"},
        {"user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0", "vendor": "Google Inc.", "renderer": "ANGLE (Intel HD Graphics)"}
    ]

    def generate_spoofed_profile(self) -> Dict[str, str]:
        """Constructs an unlinked client metadata envelope."""
        base = random.choice(self.FINGERPRINT_PROFILES)
        return {
            "user_agent": base["user_agent"],
            "webgl_vendor": base["vendor"],
            "webgl_renderer": base["renderer"],
            "screen_resolution": random.choice(["1920x1080", "1440x900", "2560x1440"])
        }
