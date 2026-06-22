import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from utils.session_injector import SessionInjector

TMP_SESSION_DIR = Path("/tmp/test_sessions_vault")

@pytest.fixture(autouse=True)
def cleanup_env():
    if TMP_SESSION_DIR.exists():
        for f in TMP_SESSION_DIR.iterdir(): f.unlink()
        TMP_SESSION_DIR.rmdir()
    yield
    if TMP_SESSION_DIR.exists():
        for f in TMP_SESSION_DIR.iterdir(): f.unlink()
        TMP_SESSION_DIR.rmdir()

def test_session_state_serialization():
    injector = SessionInjector(storage_dir=str(TMP_SESSION_DIR))
    mock_cookies = [{"name": "session_id", "value": "xyz123", "domain": "example.com"}]
    
    success = injector.save_session_state("identity_007", cookies=mock_cookies)
    assert success is True
    
    saved_file = TMP_SESSION_DIR / "state_identity_007.json"
    assert saved_file.is_file()
    
    data = json.loads(saved_file.read_text(encoding="utf-8"))
    assert data["cookies"][0]["value"] == "xyz123"

@pytest.mark.asyncio
async def test_playwright_context_injection():
    injector = SessionInjector(storage_dir=str(TMP_SESSION_DIR))
    mock_cookies = [{"name": "auth_token", "value": "secure_token", "domain": "target.com"}]
    injector.save_session_state("identity_prod", cookies=mock_cookies)

    # Mock the internal browser context interface
    mock_context = AsyncMock()
    mock_context.add_cookies = AsyncMock()

    injection_result = await injector.inject_playwright_context(mock_context, "identity_prod")
    assert injection_result is True
    mock_context.add_cookies.assert_called_once_with(mock_cookies)
