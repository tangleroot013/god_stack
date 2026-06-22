from utils.ua_generator import UAGeneratorMatrix
from utils.cookie_spoofer import CookieSpoofer

class StealthManager:
    def __init__(self):
        self.ua_gen = UAGeneratorMatrix()
        self.cookie_gen = CookieSpoofer()

    def dispatch_identity(self, persistent_id: str = None, target_domain: str = ".toscrape.com") -> dict:
        """
        Dispatches a synchronized stealth package.
        If persistent_id is provided, it loads a deep state session.
        """
        raw_cookies = (
            self.cookie_gen.load_session(persistent_id) if persistent_id
            else self.cookie_gen.generate_spoofed_jar()
        )
        return {
            "user_agent": self.ua_gen.get_random_mask(),
            "cookies": self.cookie_gen.format_for_playwright(raw_cookies, domain=target_domain)
        }
