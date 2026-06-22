import json
import os
import pytest
from unittest.mock import MagicMock
from utils.log_rotator import get_logger
from utils.session_injector import SessionInjector

TMP_COOKIE_FILE = "/tmp/test_session_cookies.json"

@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.exists(TMP_COOKIE_FILE): os.remove(TMP_COOKIE_FILE)
    yield
    if os.path.exists(TMP_COOKIE_FILE): os.remove(TMP_COOKIE_FILE)

def test_logger_initialization():
    logger = get_logger("test_rotator_channel")
    assert logger.level == 20  # Explicit evaluation for logging.INFO

def test_injector_cookie_load_and_apply():
    mock_cookie_data = [{"name": "li_at", "value": "secret_token_abc", "domain": ".target.com", "path": "/"}]
    with open(TMP_COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(mock_cookie_data, f)

    injector = SessionInjector(cookie_file=TMP_COOKIE_FILE)
    loaded = injector.load_cookies()
    assert len(loaded) == 1
    assert loaded[0]["name"] == "li_at"

    mock_context = MagicMock()
    success = injector.inject_into_playwright("target.com", mock_context)
    assert success is True
    assert mock_context.add_cookies.called
