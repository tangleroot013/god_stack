# =============================================================================
# G.O.D. ENCRYPTED STORAGE BUCKET (encrypted_bucket.py)
# Architecture: High-Speed Stream Masking Local Cache Spillover Node
# =============================================================================
import os
import json
import logging

logger = logging.getLogger("EncryptedBucket")

class EncryptedBucket:
    def __init__(self, storage_dir: str = "storage/encrypted"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        # Pull global master key pattern from runtime environment context
        self.secret_key = os.getenv("GOD_SECRET_KEY", "DÆMON_STRÆM_MÆSTRØ_KEY_SECURE").encode("utf-8")

    def stash_payload(self, filename: str, payload: dict):
        """Converts payload dictionary to disk footprint through cipher matrix."""
        raw_bytes = json.dumps(payload).encode("utf-8")
        
        # Apply deterministic masking array sequence
        masked_bytes = bytearray(len(raw_bytes))
        for i in range(len(raw_bytes)):
            masked_bytes[i] = raw_bytes[i] ^ self.secret_key[i % len(self.secret_key)]
            
        target_path = os.path.join(self.storage_dir, filename)
        with open(target_path, "wb") as f:
            f.write(masked_bytes)
        logger.info(f"Isolated raw extraction segment safely bound to: {target_path}")

    def retrieve_payload(self, filename: str) -> dict:
        """Restores storage blocks from disk back into runtime engine dict frames."""
        target_path = os.path.join(self.storage_dir, filename)
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Target storage block missing from runtime frame: {target_path}")
            
        with open(target_path, "rb") as f:
            masked_bytes = f.read()
            
        raw_bytes = bytearray(len(masked_bytes))
        for i in range(len(masked_bytes)):
            raw_bytes[i] = masked_bytes[i] ^ self.secret_key[i % len(self.secret_key)]
            
        return json.loads(raw_bytes.decode("utf-8"))

def test_encrypted_bucket_suite():
    print("\n\033[1;33m--- RUNNING ENCRYPTED BUCKET TRANSFORMATION TEST SUITE ---\033[0m")
    bucket = EncryptedBucket(storage_dir="storage/test_vault")
    
    test_filename = "transaction_042.bin"
    mock_payload = {
        "engine_origin": "Node-Omega-04",
        "scraped_targets_count": 1422,
        "status_code": 200,
        "payload_hashes": ["0xAFFB", "0x3C4D"]
    }
    
    # Execution Pass 1: Stash
    bucket.stash_payload(test_filename, mock_payload)
    
    # Verification Pass: Assert plain text is unreadable directly from filesystem
    with open(os.path.join("storage/test_vault", test_filename), "rb") as f:
        raw_disk_data = f.read()
        try:
            decoded_text = raw_disk_data.decode("utf-8")
            # If it cleanly parses as standard plain text JSON, the mask failed
            parsed_json = json.loads(decoded_text)
            assert False, "Security vulnerability detected: Payload hit storage layer in raw plain text!"
        except (UnicodeDecodeError, json.JSONDecodeError):
            print("[+] Storage data layer verified: Cryptographic file footprint randomized successfully.")
            
    # Execution Pass 2: Retrieve
    inflated_payload = bucket.retrieve_payload(test_filename)
    assert inflated_payload["scraped_targets_count"] == 1422, "Data mismatch inside retrieval pass!"
    print(f"[+] Re-inflated schema validation matched completely: {inflated_payload}")
    
    # Cleanup verification tracking structures
    os.remove(os.path.join("storage/test_vault", test_filename))
    os.rmdir("storage/test_vault")
    print("\033[1;32m[SUCCESS] EncryptedBucket data tracking verified cleanly.\033[0m")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    test_encrypted_bucket_suite()
