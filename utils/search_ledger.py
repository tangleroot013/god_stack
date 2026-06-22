import json
import hashlib
from pathlib import Path
from utils.log_rotator import get_logger

log = get_logger("SearchLedger")

class SearchLedger:
    METADATA_FILE = Path("/home/tangleroot013/god_stack/.ledger_meta.json")

    def __init__(self, vault_dir: str):
        self.vault_dir = Path(vault_dir)
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.index = {}  # inverted memory index mapping: {file_path: token_list}
        self.metadata = {}
        self._load_metadata()

    def _load_metadata(self):
        """Loads state parameters tracking file mutation logs."""
        if self.METADATA_FILE.is_file():
            try:
                self.metadata = json.loads(self.METADATA_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                log.error(f"Error restoring ledger indices: {e}")
                self.metadata = {}

    def _save_metadata(self):
        """Saves current state tracking records cleanly."""
        try:
            self.METADATA_FILE.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")
        except Exception as e:
            log.error(f"Failed to persist state ledger profiles: {e}")

    def _calculate_checksum(self, path: Path) -> str:
        """Returns the SHA-256 hash representation of file binaries."""
        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()

    def _tokenize(self, text: str) -> list:
        """Splits raw string representations into distinct structural words."""
        return [word.strip().lower() for word in text.split() if len(word.strip()) > 1]

    def index_file(self, path: Path):
        """Processes an individual markdown file if it has missing or mutated state profiles."""
        path = Path(path)
        if not path.exists():
            return False

        checksum = self._calculate_checksum(path)
        path_str = str(path)

        if self.metadata.get(path_str) == checksum and path_str in self.index:
            # Short-circuit processing loop if file matches existing structures perfectly
            return False

        try:
            text_content = path.read_text(encoding="utf-8")
            tokens = self._tokenize(text_content)
            self.index[path_str] = tokens
            
            # Enforce state update logs
            self.metadata[path_str] = checksum
            self._save_metadata()
            log.info(f"💾 File token structures indexed incrementally: {path.name}")
            return True
        except Exception as e:
            log.error(f"Error building token schema map arrays: {e}")
            return False
