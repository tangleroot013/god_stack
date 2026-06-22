import os
import shutil
import logging
from typing import List

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[OBSIDIAN-BRIDGE]\033[0m %(message)s")
logger = logging.getLogger("ObsidianBridge")

class ObsidianBridge:
    """Synchronizes the SearchLedger index with an external Obsidian vault."""
    def __init__(self, stack_vault="/home/tangleroot013/god_stack/outputs/vault", obsidian_vault=None):
        self.stack_vault = stack_vault
        self.obsidian_vault = obsidian_vault

    def sync_payloads(self):
        """Mirrors generated Markdown files to the targeted Obsidian environment."""
        if not self.obsidian_vault or not os.path.exists(self.obsidian_vault):
            logger.warning("⚠️ Obsidian target vault path not configured or missing. Skipping sync.")
            return

        if not os.path.exists(self.stack_vault):
            logger.warning("⚠️ Source stack vault directory is missing. Nothing to sync.")
            return

        synced_count = 0
        for filename in os.listdir(self.stack_vault):
            if filename.endswith(".md"):
                src = os.path.join(self.stack_vault, filename)
                dest = os.path.join(self.obsidian_vault, filename)

                # Preserves metadata timestamps during block copying
                shutil.copy2(src, dest)
                synced_count += 1
                logger.info(f"🔄 Synced note link: [[{filename[:-3]}]] to Obsidian vault.")
        
        logger.info(f"✨ Mirror matrix complete. Total files processed: {synced_count}")

    def create_moc(self, query_results: List[dict], moc_name="Intelligence Index"):
        """Generates an organized Map of Content (MOC) tracking note index."""
        if not self.obsidian_vault or not os.path.exists(self.obsidian_vault):
            return

        moc_path = os.path.join(self.obsidian_vault, f"{moc_name}.md")
        with open(moc_path, "w", encoding="utf-8") as f:
            f.write(f"# {moc_name}\n\n")
            f.write("## Recent Captures Ledger\n")
            for hit in query_results:
                # Extract clean base filename from absolute path parameters
                base_name = os.path.basename(hit.get('path', 'Unknown_Node'))
                clean_link = base_name[:-3] if base_name.endswith(".md") else base_name
                f.write(f"- [[{clean_link}]]\n")
        logger.info(f"🗺️ Generated map file: {moc_name}.md inside graph workspace.")
