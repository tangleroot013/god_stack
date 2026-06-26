import os
import shutil
import hashlib
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[OBSIDIAN-OPTIMIZED]\033[0m %(message)s")
logger = logging.getLogger("ObsidianBridge")

class ObsidianBridge:
    """Synchronizes the SearchLedger index with an external Obsidian vault with delta hashing."""
    def __init__(self, stack_vault="/home/tangleroot013/god_stack/outputs/vault", obsidian_vault=None, min_density=0.8):
        self.stack_vault = stack_vault
        self.obsidian_vault = obsidian_vault
        self.min_density = min_density

    def _compute_sha256(self, file_path: str) -> str:
        """Calculates file checksums to prevent unnecessary disk overwrites."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def _parse_density(self, file_path: str) -> float:
        """Extracts quality metrics embedded inside note frontmatter metadata headers."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "density:" in line.lower() or "quality_score:" in line.lower():
                        parts = line.split(":")
                        if len(parts) > 1:
                            return float(parts[1].strip())
        except Exception:
            pass
        return 1.0  # Default fallback to permit file passing if unmeasured

    def sync_payloads(self):
        """Mirrors high-value files using delta-verification checks."""
        if not self.obsidian_vault or not os.path.exists(self.obsidian_vault):
            logger.warning("⚠️ Obsidian target vault path not configured or missing. Skipping sync.")
            return

        os.makedirs(self.obsidian_vault, exist_ok=True)

        synced_count = 0
        skipped_count = 0
        filtered_count = 0

        for filename in os.listdir(self.stack_vault):
            if filename.endswith(".md"):
                src = os.path.join(self.stack_vault, filename)
                dest = os.path.join(self.obsidian_vault, filename)

                # Refinement 1: Quality Density Threshold Filter
                density = self._parse_density(src)
                if density < self.min_density:
                    filtered_count += 1
                    continue

                # Refinement 2: Checksum-backed Delta Hashing Verification
                if os.path.exists(dest):
                    if self._compute_sha256(src) == self._compute_sha256(dest):
                        skipped_count += 1
                        continue

                shutil.copy2(src, dest)
                synced_count += 1
                logger.info(f"🔄 Delta Synced note: [[{filename[:-3]}]]")
        
        logger.info(f"📊 Sync Metrics Summary -> Synced: {synced_count} | Untouched: {skipped_count} | Low-Density Filtered: {filtered_count}")
