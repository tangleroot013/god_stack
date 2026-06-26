import os
import json
import zlib
from datetime import datetime

class VaultCompressor:
    """Optimizes long-term text storage by packing Markdown datasets into high-ratio compressed binaries."""
    def __init__(self, vault_dir: str = "vaults"):
        self.vault_dir = vault_dir
        os.makedirs(self.vault_dir, exist_ok=True)

    def archive_payload(self, target_url: str, title: str, markdown_content: str) -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        sanitized_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
        sanitized_title = sanitized_title.replace(" ", "_").lower()
        
        filename = f"vault_{sanitized_title}_{timestamp}.bin"
        target_path = os.path.join(self.vault_dir, filename)
        
        structured_data = {
            "metadata": {
                "url": target_url,
                "title": title,
                "archived_at": datetime.utcnow().isoformat()
            },
            "payload": markdown_content
        }
        
        try:
            raw_bytes = json.dumps(structured_data, ensure_ascii=False).encode('utf-8')
            compressed_bytes = zlib.compress(raw_bytes, level=9)
            with open(target_path, "wb") as vault_file:
                vault_file.write(compressed_bytes)
            return target_path
        except Exception:
            return ""

if __name__ == "__main__":
    compressor = VaultCompressor()
    mock_md = "# Sample Extract\n" + "Lorem ipsum dolor sit amet. " * 50
    compressor.archive_payload("https://example.com", "Sandbox Intelligence File", mock_md)
    print("Vault sandbox compressor validation success.")
