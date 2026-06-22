import pytest
import json
from pathlib import Path
from utils.proxy_shuffler import ProxyRotationPool, FingerprintShuffler

TMP_PROXY_CONF = Path("/tmp/test_proxies.json")

@pytest.fixture(autouse=True)
def run_around():
    mock_data = {
        "proxies": [
            {"host": "192.168.1.100", "port": 3128, "username": "alpha", "password": "key"}
        ]
    }
    TMP_PROXY_CONF.write_text(json.dumps(mock_data), encoding="utf-8")
    yield
    if TMP_PROXY_CONF.exists():
        TMP_PROXY_CONF.unlink()

def test_proxy_pool_isolation():
    pool = ProxyRotationPool(proxy_config_path=str(TMP_PROXY_CONF))
    selected = pool.get_isolated_proxy()
    
    assert selected["host"] == "192.168.1.100"
    assert selected["port"] == 3128
    assert selected["username"] == "alpha"

def test_fingerprint_generation():
    shuffler = FingerprintShuffler()
    profile = shuffler.generate_spoofed_profile()
    
    assert "user_agent" in profile
    assert "webgl_vendor" in profile
    assert "webgl_renderer" in profile
    assert "screen_resolution" in profile
