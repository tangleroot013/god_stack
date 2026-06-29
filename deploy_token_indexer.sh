#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Initializing Structural Token Frequency Indexer...\033[0m"

cat << 'PYEOF' > token_indexer.py
import collections
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[TOKEN-INDEX]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TokenIndexer")

class StructuralTokenFrequencyIndexer:
    def compute_density_profile(self, target_text: str) -> dict:
        print("\n\033[1;32m--- G.O.D. SEMANTIC DENSITY PROFILE CALCULATION ---\033[0m")
        normalized_tokens = re.findall(r'\w+', target_text.lower())
        frequency_map = collections.Counter(normalized_tokens)
        
        logger.info(f"Analyzing extracted payload string fragment matrix... Found {len(normalized_tokens)} tokens.")
        for token, count in frequency_map.most_common(2):
            logger.info(f"  High-Density Token Found -> [ \033[1;33m{token}\033[0m ]: Occurrences = {count}")
            
        return dict(frequency_map)

if __name__ == "__main__":
    indexer = StructuralTokenFrequencyIndexer()
    sample_segment = "payload active payload initial status payload sync status"
    indexer.compute_density_profile(sample_segment)
    print("\n\033[1;32m✔ MODULE 88 CONTENT TOKEN DENSITY METRICS LIVE.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Testing textual metrics evaluation maps...\033[0m"
chmod +x token_indexer.py
./.venv/bin/python3 token_indexer.py
