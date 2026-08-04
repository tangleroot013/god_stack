#!/usr/bin/env python3
# ==============================================================================
# kb_generator.py – SHA-256 payload signatures
# ==============================================================================
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[KB-GEN]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("KBGenerator")

class KBGenerator:
    def generate(self, payload: str) -> str:
        sig = hashlib.sha256(payload.encode()).hexdigest()[:16]
        logger.info(f"🔐 Generated signature: {sig}")
        return sig

if __name__ == "__main__":
    kb = KBGenerator()
    print(kb.generate("sample payload"))
