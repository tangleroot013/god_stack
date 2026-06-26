import json
import logging
from pathlib import Path
from typing import Any, Dict, List

log = logging.getLogger("SessionInjector")

class SessionInjector:
    """Manages collection and injection of authenticated state jars into browser contexts."""
    
    def __init__(self, storage_dir="/home/tangleroot013/god_stack/secure/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_session_state(self, identity_id: str, cookies: List[Dict[str, Any]], local_storage: Dict[str, Any] = None) -> bool:
        """Persists an authenticated state matrix securely to disk."""
        try:
            state_payload = {
                "cookies": cookies,
                "local_storage": local_storage or {},
                "updated_at": Path("/home/tangleroot013/god_stack").stat().st_mtime
            }
            target_path = self.storage_dir / f"state_{identity_id}.json"
            target_path.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")
            log.info(f"💾 Authenticated state jar archived for identity: {identity_id}")
            return True
        except Exception as e:
            log.error(f"Failed to save session state: {e}")
            return False

    async def inject_playwright_context(self, context: Any, identity_id: str) -> bool:
        """Injects preserved cookies and session metrics into a Playwright browser context."""
        target_path = self.storage_dir / f"state_{identity_id}.json"
        if not target_path.is_file():
            log.warning(f"⚠️ No session profile found for identity: {identity_id}")
            return False

        try:
            state_data = json.loads(target_path.read_text(encoding="utf-8"))
            
            # Inject standard cookies session array
            await context.add_cookies(state_data.get("cookies", []))
            
            # Local storage payload staging must be handled via a page routing script injection
            log.info(f"🚀 Session state matrix injected into worker context for: {identity_id}")
            return True
        except Exception as e:
            log.error(f"Session injection vector execution fault: {e}")
            return False
