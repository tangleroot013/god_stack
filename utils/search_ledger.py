import os
import re
import json
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[SEARCH-LEDGER]\033[0m %(message)s")
logger = logging.getLogger("SearchLedger")

class SearchLedger:
    """Compiles local index maps and runs text/regex search queries over markdown vaults."""
    def __init__(self, vault_dir="/home/tangleroot013/god_stack/outputs/vault"):
        self.vault_dir = vault_dir
        self.index_cache: Dict[str, str] = {}

    def rebuild_index(self) -> int:
        """Scans the vault directory and builds a flat in-memory data ledger."""
        self.index_cache.clear()
        if not os.path.exists(self.vault_dir):
            return 0

        for root, _, files in os.walk(self.vault_dir):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            self.index_cache[file_path] = f.read()
                    except Exception as e:
                        logger.error(f"Failed to index file {file_path}: {e}")
        
        logger.info(f"💾 Index compiled. Total entries tracked: {len(self.index_cache)}")
        return len(self.index_cache)

    def query(self, pattern: str, is_regex: bool = False) -> List[Dict[str, Any]]:
        """Scans the index map for direct keyword hits or raw regex expressions."""
        results = []
        
        try:
            search_regex = re.compile(pattern, re.IGNORECASE) if is_regex else None
        except re.error as e:
            logger.error(f"Invalid regex pattern supplied: {e}")
            return []

        for path, content in self.index_cache.items():
            if is_regex and search_regex:
                matches = search_regex.findall(content)
                if matches:
                    results.append({"path": path, "matches_count": len(matches), "preview": content[:150].strip()})
            else:
                if pattern.lower() in content.lower():
                    count = content.lower().count(pattern.lower())
                    results.append({"path": path, "matches_count": count, "preview": content[:150].strip()})

        return results
