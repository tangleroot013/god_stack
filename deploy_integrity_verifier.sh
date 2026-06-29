#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating Outbound Payload Integrity Hash Verifier...\033[0m"

cat << 'PYEOF' > integrity_verifier.py
import hashlib
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[INTEG-VERIFY]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("IntegVerify")

class PayloadIntegrityVerifier:
    def append_integrity_hash(self, raw_data: dict) -> dict:
        print("\n\033[1;32m--- G.O.D. DATA INTEGRITY SIGNATURE GENERATOR ---\033[0m")
        serialized = json.dumps(raw_data, sort_keys=True).encode('utf-8')
        payload_hash = hashlib.sha256(serialized).hexdigest()
        
        logger.info("Computing SHA-256 payload integrity validation key...")
        logger.info(f"  Generated Verification Hash: \033[1;34m{payload_hash}\033[0m")
        
        signed_payload = {"payload": raw_data, "integrity_hash": payload_hash}
        return signed_payload

if __name__ == "__main__":
    verifier = PayloadIntegrityVerifier()
    sample_block = {"session_id": "SESS_KEY_9921", "sequence_index": 78, "status": "NOMINAL"}
    verifier.append_integrity_hash(sample_block)
    print("\n\033[1;32m✔ MODULE 78 PAYLOAD SIGNATURE INTEGRITY MATRIX READY.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Validating integrity hashing operations...\033[0m"
chmod +x integrity_verifier.py
./.venv/bin/python3 integrity_verifier.py
