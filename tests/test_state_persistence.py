import pytest
import os
import shutil
from utils.cookie_spoofer import CookieSpoofer
from utils.stealth_manager import StealthManager

TMP_SESSIONS = "/tmp/god_sessions"

@pytest.fixture(autouse=True)
def run_around_tests():
    if os.path.exists(TMP_SESSIONS): shutil.rmtree(TMP_SESSIONS)
    yield
    if os.path.exists(TMP_SESSIONS): shutil.rmtree(TMP_SESSIONS)

def test_session_save_and_recall():
    spoofer = CookieSpoofer(session_dir=TMP_SESSIONS)
    mock_jar = {"session_id_xyz": "authenticated_secret_token"}
    
    spoofer.save_session("high_value_identity", mock_jar)
    recalled_jar = spoofer.load_session("high_value_identity")
    
    assert recalled_jar["session_id_xyz"] == "authenticated_secret_token"

def test_stealth_manager_playwright_formatting():
    sm = StealthManager()
    identity = sm.dispatch_identity(persistent_id=None)
    
    assert isinstance(identity["cookies"], list)
    assert "name" in identity["cookies"][0]
    assert "domain" in identity["cookies"][0]
