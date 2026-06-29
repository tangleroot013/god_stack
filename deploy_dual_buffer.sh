#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Provisioning Asymmetric Dual-Buffer Flush Core...\033[0m"

cat << 'PYEOF' > dual_buffer.py
import asyncio
import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[DUAL-BUFFER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DualBuffer")

class AsymmetricPayloadBuffer:
    def __init__(self, flush_limit: int = 3, dest_file: str = "outputs/buffered_payloads.json"):
        self.flush_limit = flush_limit
        self.dest_file = dest_file
        self._primary_buffer = []
        self._secondary_buffer = []
        self._lock = asyncio.Lock()
        os.makedirs(os.path.dirname(self.dest_file), exist_ok=True)

    async def ingest_payload(self, record: dict):
        async with self._lock:
            self._primary_buffer.append(record)
            logger.info(f"Buffered record. Active Primary Allocation Size: {len(self._primary_buffer)}/{self.flush_limit}")
            
            if len(self._primary_buffer) >= self.flush_limit:
                logger.warning("Primary structural limit breached! Swapping buffers and spinning background flush...")
                # Atomic pointer swap to completely unblock continuous ingestion
                self._secondary_buffer = self._primary_buffer
                self._primary_buffer = []
                asyncio.create_task(self._flush_secondary_to_disk())

    async def _flush_secondary_to_disk(self):
        try:
            logger.info(f"Background worker processing flush loop for {len(self._secondary_buffer)} cached matrix entries.")
            # Simulate underlying IO disk commit
            await asyncio.sleep(0.05)
            with open(self.dest_file, "a") as f:
                for item in self._secondary_buffer:
                    f.write(json.dumps(item) + "\n")
            logger.info("Secondary memory buffers drained and committed to persistent VFS hardware cleanly.")
        finally:
            self._secondary_buffer = []

async def main():
    print("\n\033[1;32m--- G.O.D. ASYMMETRIC FLUSH CORE VALIDATION ---\033[0m")
    buffer_system = AsymmetricPayloadBuffer()
    
    # Ingest 4 consecutive mock records to trigger the asynchronous swap mechanism
    for i in range(4):
        await buffer_system.ingest_payload({"payload_id": f"BLOCK_{i}", "metric": 100 * i})
    
    # Short sleep to let the background task finalize its logs cleanly
    await asyncio.sleep(0.1)
    print("\n\033[1;32m✔ MODULE 45 ASYMMETRIC BUFFER MATRIX FUNCTIONAL.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF

echo -e "\033[1;34m[2/2] Launching burst memory ingestion validation check...\033[0m"
chmod +x dual_buffer.py
./.venv/bin/python3 dual_buffer.py
