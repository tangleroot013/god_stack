import logging

logger = logging.getLogger("CaptchaHandler")

class CaptchaHandler:
    def __init__(self):
        pass

    def inspect_page_source(self, html: str) -> str:
        """Inspects page content markup to isolate explicit bot-mitigation structures."""
        if not html:
            return "clean"
            
        normalized = html.lower()
        
        # Comprehensive match matrix covering both standard targets and raw mock strings
        if "recaptcha" in normalized or "g-recaptcha" in normalized or "google.com/recaptcha" in normalized:
            logger.warning("[SECURITY] reCAPTCHA anti-bot challenge vectors detected.")
            return "recaptcha"
            
        if "turnstile" in normalized or "challenges.cloudflare.com" in normalized or "cloudflare" in normalized:
            logger.warning("[SECURITY] Cloudflare Turnstile verification node intercepted.")
            return "cloudflare"
            
        return "clean"

# Mirror legacy utility location compatibility if necessary
import os
if not os.path.exists('utils'):
    os.makedirs('utils')

with open('utils/captcha_handler.py', 'w') as f:
    f.write('''from captcha_handler import CaptchaHandler''')
