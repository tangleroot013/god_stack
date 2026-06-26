# =============================================================================
# G.O.D. STACK CORE REGRESSION TEST SUITE (test_core_utilities.py)
# Architecture: Unittest Verification Framework for Processing Pipelines
# =============================================================================

import unittest
from utils.url_sanitizer import UrlSanitizer
from utils.captcha_handler import CaptchaHandler

class TestUrlSanitizer(unittest.TestCase):
    """Verifies robustness and spec compliance of the string sanitization matrix."""

    def test_case_insensitive_schemes(self):
        """Ensure variant casing schemes normalize down to standard lower baseline."""
        input_url = "HTTPS://NEWS.YCOMBINATOR.COM/item?id=1"
        expected = "https://news.ycombinator.com/item?id=1"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_missing_scheme_prepend(self):
        """Ensure raw host configurations receive automatic safe fallback schemes."""
        input_url = "news.ycombinator.com/news"
        expected = "https://news.ycombinator.com/news"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_tracking_parameter_removal(self):
        """Verify analytics markers are completely stripped while core identifiers stay intact."""
        input_url = "https://news.ycombinator.com/item?id=45&utm_source=twitter&fbclid=xyz123"
        expected = "https://news.ycombinator.com/item?id=45"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)

    def test_fragment_stripping(self):
        """Confirm trailing browser fragment hash links are omitted from backend calls."""
        input_url = "https://news.ycombinator.com/front#comments-section"
        expected = "https://news.ycombinator.com/front"
        self.assertEqual(UrlSanitizer.normalize(input_url), expected)


class TestCaptchaHandler(unittest.TestCase):
    """Tests passive element detection parameters and defensive signature bridges."""

    def setUp(self):
        self.handler = CaptchaHandler()

    def test_clean_html_evaluation(self):
        """Verify safe structural markup logs as non-threatening."""
        clean_dom = "<html><body><h1>Standard Text Layout</h1></body></html>"
        self.assertEqual(self.handler.inspect_page_source(clean_dom), "clean")

    def test_cloudflare_turnstile_detection(self):
        """Ensure standard Cloudflare challenge scripts activate the matching alert profile."""
        blocked_dom = "<div><script src='https://challenges.cloudflare.com/turnstile/v0/api.js'></script></div>"
        self.assertEqual(self.handler.inspect_page_source(blocked_dom), "cloudflare")

    def test_recaptcha_detection(self):
        """Ensure reCAPTCHA dynamic frame injections trigger detection profiles."""
        blocked_dom = "<iframe src='https://www.google.com/recaptcha/api2/bframe'></iframe>"
        self.assertEqual(self.handler.inspect_page_source(blocked_dom), "recaptcha")

if __name__ == "__main__":
    unittest.main()
