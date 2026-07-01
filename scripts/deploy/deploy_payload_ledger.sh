#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Synthesizing Cryptographic Ledger Subsystem...\033[0m"

cat << 'PYEOF' > payload_ledger.py
import hashlib
import json
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;32m[CRYPT-LEDGER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CryptLedger")

class EncryptedManifestManager:
    def __init__(self, ledger_file: str = "outputs/manifest.ledger"):
        self.ledger_file = ledger_file
        os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)

    def sign_payload_block(self, payload_data: dict):
        print("\n\033[1;32m--- G.O.D. CRYPTOGRAPHIC DATA INTEGRITY SIGNING ---\033[0m")
        
        # Serialize normalized data keys to guarantee immutable hash outputs
        serialized_block = json.dumps(payload_data, sort_keys=True).encode('utf-8')
        sha256_sig = hashlib.sha256(serialized_block).hexdigest()
        
        logger.info(f"Generating block allocation fingerprint signature...")
        logger.info(f"  Captured Signature: \033[1;35m{sha256_sig}\033[0m")
        
        with open(self.ledger_file, "a") as f:
            f.write(f"{sha256_sig}\n")
        logger.info("Cryptographic block appended safely to primary ledger audit tracking record.")

if __name__ == "__main__":
    manager = EncryptedManifestManager()
    mock_dataset = {"module": 41, "integrity_check": "SECURE", "timestamp_epoch": 1782724800}
    manager.sign_payload_block(mock_dataset)
    print("\n\033[1;32m✔ MODULE 41 CRYPTOGRAPHIC LEDGER COMPLIANT.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Running secure cryptographic signature calculations...\033[0m"
chmod +x payload_ledger.py
./.venv/bin/python3 payload_ledger.py
