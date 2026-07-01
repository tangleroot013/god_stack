import json
import os
from datetime import datetime

class DeadLetterStream:
    @staticmethod
    def contain(url: str, error_context: str):
        os.makedirs("outputs", exist_ok=True)
        entry = {
            "url": url,
            "error": error_context,
            "timestamp": datetime.utcnow().isoformat()
        }
        with open("outputs/dead_letter_vault.jsonl", "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"\033[0;31m[DLQ] Node quarantined: {url} | Reason: {error_context}\033[0m")
