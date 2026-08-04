import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[LOG-ROTATER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("LogRotater")

class StructuredLogRotater:
    def __init__(self, target_file: str = "storage/flushed_ledger.log", max_bytes: int = 1024):
        self.target_file = target_file
        self.max_bytes = max_bytes

    def evaluate_rotation(self):
        print("\n\033[1;32m--- G.O.D. LOCAL STORAGE RETENTION MAINTENANCE ---\033[0m")
        if not os.path.exists(self.target_file):
            logger.info("Target ledger log file does not exist yet. Skipping check.")
            return

        file_size = os.path.getsize(self.target_file)
        logger.info(f"Auditing file capacity footprint: {file_size} / {self.max_bytes} maximum allowed bytes.")
        
        if file_size >= self.max_bytes:
            archive_name = f"{self.target_file}.old"
            os.rename(self.target_file, archive_name)
            logger.warning(f"  Threshold exceeded! File rotated cleanly to destination: \033[1;34m{archive_name}\033[0m")
        else:
            logger.info("  File scope stays within safety margins. Rotation skipped.")

if __name__ == "__main__":
    rotater = StructuredLogRotater()
    rotater.evaluate_rotation()
    print("\n\033[1;32m✔ MODULE 93 DATARETENTION MECHANICS SECURED.\033[0m\n")
