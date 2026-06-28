import logging

class CaptchaHandler:
    def __init__(self): pass

    def inspect_page_source(self, html: str) -> str:
        if not html: return "clean"
        normalized = html.lower()
        if "recaptcha" in normalized or "g-recaptcha" in normalized: return "recaptcha"
        if "turnstile" in normalized or "cloudflare" in normalized: return "cloudflare"
        return "clean"
