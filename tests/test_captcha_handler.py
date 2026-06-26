import pytest
import pytest_asyncio
from utils.captcha_handler import CaptchaHandler

@pytest.fixture
def sentinel():
    return CaptchaHandler()

def test_clean_html_source(sentinel):
    assert sentinel.inspect_page_source("<html><body>Normal Page</body></html>") == "clean"

@pytest.mark.parametrize("defense,html", [
    ("cloudflare", "<html><script src='https://challenges.cloudflare.com/turnstile/v0/api.js'></script></html>"),
    ("recaptcha", "<div class='g-recaptcha' data-sitekey='mock_key'></div>"),
    ("hcaptcha", "<script src='https://hcaptcha.com/1/api.js' async defer></script>")
])
def test_anti_bot_fingerprint_detection(sentinel, defense, html):
    assert sentinel.inspect_page_source(html) == defense

@pytest.mark.asyncio
async def test_solver_bridge_routing(sentinel):
    """Validates that the async bridge returns an auth token."""
    token = await sentinel.deploy_solver_bridge("cloudflare", "https://example.com")
    assert isinstance(token, str)
    assert token == "MOCK_AUTH_TOKEN_B64_DATA"
