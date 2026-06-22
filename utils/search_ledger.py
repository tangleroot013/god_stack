import os
import json
import logging
from pathlib import Path

log = logging.getLogger("SearchLedger")

class SearchLedger:
    """Compiles local index maps using differential scanning logic for fast retrieval."""
    def __init__(self, vault_dir="/home/tangleroot013/god_stack/outputs/vault"):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.vault_dir / ".state_ledger.json"
        self.index_cache = {}
        self.file_states = self._load_state()

    def _load_state(self) -> dict:
        """Loads historical modification timestamps to facilitate differential scans."""
        if self.state_file.is_file():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except Exception as e:
                return {}
        return {}

    def _save_state(self):
        """Anchors the current vault state metadata to disk."""
        try:
            self.state_file.write_text(json.dumps(self.file_states, indent=2), encoding="utf-8")
        except Exception as e:
            pass

    def rebuild_index(self) -> int:
        """Differential scanner: only parses new or modified files."""
        new_files_indexed = 0
        
        if not self.vault_dir.exists():
            return 0

        # Gather target files within vault directory limits
        current_files = [f for f in os.listdir(self.vault_dir) if f.endswith(".md")]

        for filename in current_files:
            filepath = self.vault_dir / filename
            try:
                mtime = os.path.getmtime(filepath)
            except OSError:
                continue

            # Check if the asset timestamp matches file parameters exactly
            if filename not in self.file_states or mtime > self.file_states[filename]:
                try:
                    self.index_cache[filename] = filepath.read_text(encoding="utf-8")
                    self.file_states[filename] = mtime
                    new_files_indexed += 1
                except Exception:
                    continue

        if new_files_indexed > 0:
            self._save_state()
            
        return len(self.index_cache)
