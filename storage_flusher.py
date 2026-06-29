import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[STORAGE-FLUSH]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("StorageFlusher")

class MemoryMappedStorageFlusher:
    def __init__(self, capacity_limit: int = 3, target_file: str = "storage/flushed_ledger.log"):
        self.capacity_limit = capacity_limit
        self.target_file = target_file
        self.staging_buffer = []
        os.makedirs(os.path.dirname(self.target_file), exist_ok=True)

    def accumulate_record(self, data_record: dict):
        print("\n\033[1;32m--- G.O.D. MEMORY STORAGE BATCH COMMIT ENGINE ---\033[0m")
        self.staging_buffer.append(data_record)
        logger.info(f"Staged transaction record into memory array. Pool capacity: {len(self.staging_buffer)}/{self.capacity_limit}")
        
        if len(self.staging_buffer) >= self.capacity_limit:
            logger.warning("\033[1;33mMemory accumulation threshold reached. Flushing bulk storage arrays to disk...\033[0m")
            with open(self.target_file, "a") as f:
                for item in self.staging_buffer:
                    f.write(json.dumps(item) + "\n")
            logger.info(f"  Successfully committed entries to permanent file node: {self.target_file}")
            self.staging_buffer.clear()

if __name__ == "__main__":
    flusher = MemoryMappedStorageFlusher()
    # Simulate adding records sequentially until a flush triggers
    flusher.accumulate_record({"event": "INIT", "code": 1})
    flusher.accumulate_record({"event": "ROUTE_LOCK", "code": 5})
    flusher.accumulate_record({"event": "CLEAN_EXIT", "code": 0})
    print("\n\033[1;32m✔ MODULE 92 RECORD FLUSH STORAGE CONTROLLERS STABLE.\033[0m\n")
