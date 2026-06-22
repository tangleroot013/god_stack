import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from cron.token_refresher import TokenRefresherCron

TMP_CRON_DIR = Path("/tmp/test_cron_vault")

@pytest.fixture(autouse=True)
def cleanup_env():
    if TMP_CRON_DIR.exists():
        for f in TMP_CRON_DIR.iterdir(): f.unlink()
        TMP_CRON_DIR.rmdir()
    TMP_CRON_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TMP_CRON_DIR.exists():
        for f in TMP_CRON_DIR.iterdir(): f.unlink()
        TMP_CRON_DIR.rmdir()

def test_fresh_token_bypass():
    refresher = TokenRefresherCron(storage_dir=str(TMP_CRON_DIR), refresh_window_seconds=3600)
    
    # Generate an expiration date far into the future
    future_time = datetime.now(timezone.utc).timestamp() + 86400
    mock_payload = {
        "cookies": [{"name": "auth", "value": "valid", "expires": future_time}],
        "local_storage": {}
    }
    
    target_path = TMP_CRON_DIR / "state_id_fresh.json"
    target_path.write_text(json.dumps(mock_payload))
    
    assert refresher.check_identity_stale(target_path) is False

def test_stale_token_trigger():
    refresher = TokenRefresherCron(storage_dir=str(TMP_CRON_DIR), refresh_window_seconds=3600)
    
    # Generate an expiration timestamp that falls within the refresh window
    near_expiry = datetime.now(timezone.utc).timestamp() + 1800
    mock_payload = {
        "cookies": [{"name": "auth", "value": "expiring", "expires": near_expiry}],
        "local_storage": {}
    }
    
    target_path = TMP_CRON_DIR / "state_id_stale.json"
    target_path.write_text(json.dumps(mock_payload))
    
    assert refresher.check_identity_stale(target_path) is True
