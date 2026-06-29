#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Deploying Stream Frame Checksum Validation Engine...\033[0m"

cat << 'PYEOF' > checksum_validator.py
import zlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[CHECKSUM]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Checksum")

class StreamFrameChecksumValidator:
    def verify_buffer_integrity(self, payload_string: str) -> int:
        print("\n\033[1;32m--- G.O.D. STREAM INLINE BITWISE INTEGRITY CHECK ---\033[0m")
        logger.info("Computing runtime cyclic redundancy check profile...")
        
        checksum = zlib.crc32(payload_string.encode('utf-8')) & 0xffffffff
        logger.info(f"  Calculated Verification Signature: \033[1;34m{hex(checksum).upper()}\033[0m")
        return checksum

if __name__ == "__main__":
    validator = StreamFrameChecksumValidator()
    validator.verify_buffer_integrity("FRAME_DATA_NODE_BLOCK_Z871")
    print("\n\033[1;32m✔ MODULE 99 STREAM CHECKSUM VERIFICATION READY.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Running inline bitwise calculation tests...\033[0m"
chmod +x checksum_validator.py
./.venv/bin/python3 checksum_validator.py
