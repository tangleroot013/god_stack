import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict

log = logging.getLogger("TokenRefresher")

class TokenRefresherCron:
    """Monitors cookie expiration fields and runs updates on aging contexts."""
    
    def __init__(self, storage_dir="/home/tangleroot013/god_stack/secure/sessions", refresh_window_seconds=14400):
        self.storage_dir = Path(storage_dir)
        self.refresh_window_seconds = refresh_window_seconds

    def check_identity_stale(self, state_path: Path) -> bool:
        """Determines if a stored session payload falls inside the refresh window."""
        try:
            payload = json.loads(state_path.read_text(encoding="utf-8"))
            cookies = payload.get("cookies", [])
            
            if not cookies:
                return True

            # Extract the earliest cookie expiration timestamp
            expiries = [c["expires"] for c in cookies if "expires" in c and isinstance(c["expires"], (int, float))]
            if not expiries:
                return False

            earliest_expiry = min(expiries)
            current_time = datetime.now(timezone.utc).timestamp()
            
            # Identify if cookie lifecycle matches maintenance parameters
            if (earliest_expiry - current_time) <= self.refresh_window_seconds:
                return True
            return False
        except Exception as e:
            log.error(f"Error checking lifecycle thresholds for {state_path.name}: {e}")
            return True

    def execute_refresh_cycle(self) -> int:
        """Scans session registries and flags items that need an update pass."""
        stale_count = 0
        target_files = list(self.storage_dir.glob("state_*.json"))

        for state_file in target_files:
            if self.check_identity_stale(state_file):
                log.info(f"🔄 Identity tracking state requires active cycling: {state_file.name}")
                stale_count += 1
                # Execution layer hooks to headful worker contexts go here
                
        return stale_count
