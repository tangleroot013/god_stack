from utils.ua_generator import UAGeneratorMatrix
from utils.cookie_spoofer import CookieSpoofer

class StealthManager:
    """The central intelligence layer for identity masks and session injection."""
    def __init__(self):
        self.ua_gen = UAGeneratorMatrix()
        self.cookie_gen = CookieSpoofer()

    def dispatch_identity(self) -> dict:
        """Generates a complete, synchronized stealth package for a request."""
        return {
            "user_agent": self.ua_gen.get_random_mask(),
            "cookies": self.cookie_gen.generate_spoofed_jar()
        }

if __name__ == "__main__":
    sm = StealthManager()
    print(f"\033[1;32m[STEALTH SETUP]\033[0m Dispatched Package: {sm.dispatch_identity()}")
