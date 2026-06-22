import os
import logging
from datetime import datetime

log = logging.getLogger("GraphSync")

class ObsidianGraphSync:
    """Serializes cluster runtime telemetry into structured markdown for Obsidian linking."""
    
    def __init__(self, vault_path: str = "./vaults/intelligence_graph"):
        self.vault_path = vault_path
        self.identities_dir = os.path.join(vault_path, "Identities")
        os.makedirs(self.identities_dir, exist_ok=True)

    def sync_identity_node(self, health_payload: dict) -> str:
        """Generates or updates a local markdown file tracking identity lifecycle states."""
        identity_id = health_payload["identity_id"]
        file_path = os.path.join(self.identities_dir, f"{identity_id}.md")
        
        # Format links back to health status tags for visual graph mapping
        markdown_content = f"""---
type: identity_node
status: {health_payload["status"]}
success_rate: {health_payload["success_rate"]}
total_missions: {health_payload["total_missions"]}
updated_at: {health_payload["evaluated_at"]}
---

# Identity Profile: [[{identity_id}]]
- **Current Security Status:** #{health_payload["status"]}
- **Reliability Metric:** {health_payload["success_rate"] * 100}%

## Active Execution Traces
Logged update on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} targeting distributed cluster partitions.
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        log.info(f"📁 Obsidian graph updated for identity node: {identity_id}")
        return file_path
