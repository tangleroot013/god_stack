import logging

logger = logging.getLogger("CaptchaHandler")

class CaptchaHandler:
    def __init__(self):
        pass

    def inspect_page_source(self, html: str) -> str:
        """Inspects inbound DOM streams to flag known firewall injection layers."""
        if not html:
            return "clean"
        
        normalized = html.lower()
        if "recaptcha" in normalized or "g-recaptcha" in normalized:
            logger.warning("Detected reCAPTCHA barrier in target DOM context.")
            return "recaptcha"
            
        if "turnstile" in normalized or "cloudflare" in normalized:
            logger.warning("Detected Cloudflare Turnstile challenge sequence.")
            return "cloudflare"
            
        return "clean"
