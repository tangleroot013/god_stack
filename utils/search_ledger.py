import re
import json
import logging
from pathlib import Path

class SearchLedger:
    """Scans Obsidian-style markdown vaults and generates a relational adjacency matrix."""
    
    def __init__(self, vault_path: str = "vaults/intelligence_graph"):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger("SearchLedger")
        self.graph = {}

    def build_ledger(self) -> dict:
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
        return self.graph

    def export_matrix(self, output_file: str = "vaults/matrix_map.json"):
        """Dumps the adjacency matrix to a standard JSON map and validates the UI asset link."""
        out_path = Path(output_file)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=4)
        self.logger.info(f"💾 Relational matrix exported to {output_file}")
        
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
