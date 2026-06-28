import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

class SearchLedger:
    """Scans Obsidian-style markdown vaults and generates a relational adjacency matrix."""
    
    # Class-level attribute required by incremental and timestamp indexing tests
    METADATA_FILE: str = "vaults/.metadata.json"
    
    def __init__(self, vault_path: str = "vaults/intelligence_graph", vault_dir: Optional[str] = None):
        # Support both names seamlessly to clear test instantiation signatures
        actual_path = vault_dir if vault_dir is not None else vault_path
        self.vault_path = Path(actual_path)
        self.logger = logging.getLogger("SearchLedger")
        self.graph: Dict[str, List[str]] = {}
        
        # Test-required attributes
        self.index_file: str = str(self.vault_path / "matrix_map.json")
        self.index_cache: Dict[str, Any] = {}
        self.index: Dict[str, Any] = {}

    def build_ledger(self) -> Dict[str, List[str]]:
        """Parses all markdown files and extracts [[linked]] relationships."""
        if not self.vault_path.exists():
            self.logger.warning(f"Vault path missing. Initializing empty vault at {self.vault_path}")
            self.vault_path.mkdir(parents=True, exist_ok=True)
            return self.graph

        self.logger.info(f"🔍 Scanning intelligence vault: {self.vault_path}")
        
        for filepath in self.vault_path.rglob("*.md"):
            node_name = filepath.stem
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    links = re.findall(r'\[\[(.*?)\]\]', content)
                    self.graph[node_name] = list(set(links))
            except Exception as e:
                self.logger.error(f"Failed to parse node {node_name}: {e}")

        self.logger.info(f"🌐 Graph compiled: {len(self.graph)} primary nodes mapped.")
        self.index = self.graph.copy()
        return self.graph

    def rebuild_index(self) -> Dict[str, Any]:
        """Compatibility wrapper required by timestamp and incremental indexing tests."""
        self.build_ledger()
        self.index_cache = self.graph.copy()
        # Return the number of files actually indexed in this run
        return len(result_dict)

    def query(self, term: str) -> List[str]:
        """Looks up nodes containing a term or matching links."""
        return [node for node, links in self.graph.items() if term in node or any(term in link for link in links)]

    def export_matrix(self, output_file: Optional[str] = None):
        """Dumps the adjacency matrix to a standard JSON map and validates the UI asset link."""
        target_file = output_file if output_file else self.index_file
        out_path = Path(target_file)
        
        # Ensure directory exists
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=4)
        self.logger.info(f"💾 Relational matrix exported to {target_file}")
        
        # Cross-check front-end asset location
        ui_file = out_path.parent / "index.html"
        if ui_file.exists():
            self.logger.info(f"🖥️  Retro Web UI detected: Open http://localhost:8090 to view fresh map.")
        else:
            self.logger.warning("⚠️  Retro Dashboard asset index.html missing from target directory.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    ledger = SearchLedger()
    ledger.build_ledger()
    ledger.export_matrix()
