#!/usr/bin/env python3
import os
import re

class MatrixPoolLoader:
    def __init__(self):
        # Validates canonical protocol layers securely
        self.url_sentinel_regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE
        )

    def yield_targets_from_file(self, source_filepath):
        """Reads target arrays line-by-line using a generator to protect stack memory."""
        if not os.path.exists(source_filepath):
            raise FileNotFoundError(f"Target array matrix map file not found: {source_filepath}")
            
        with open(source_filepath, mode="r", encoding="utf-8") as manifest:
            for raw_line in manifest:
                cleaned_route = raw_line.strip()
                # Bypass comments or structural spaces
                if not cleaned_route or cleaned_route.startswith("#"):
                    continue
                # Enforce clean schema formatting validation
                if self.url_sentinel_regex.match(cleaned_route):
                    yield cleaned_route
                else:
                    print(f"\033[0;31m[POOL SKIP] Purged structurally malformed input line: '{cleaned_route}'\033[0m")

if __name__ == "__main__":
    # Instantiate sample operational file layout targets
    test_manifest_path = "bulk_targets.txt"
    with open(test_manifest_path, "w", encoding="utf-8") as f:
        f.write("# G.O.D. STACK BULK MANIFEST INGESTION\n")
        f.write("https://example.com/stream_node_v2_0\n")
        f.write("MALFORMED_ROUTE_STRING_PATTERN\n")
        f.write("https://example.com/stream_node_v2_1\n")

    loader = MatrixPoolLoader()
    print("\033[0;36m=== PARSING HIGH-CAPACITY DEPLOYMENT TARGET POOL ===\033[0m")
    
    active_pool = list(loader.yield_targets_from_file(test_manifest_path))
    print(f"\033[0;32m[POOL LOADED] Extraction pipeline verified {len(active_pool)} sanitized operational routes out of the target manifest.\033[0m")
    
    # Cleanup workspace
    if os.path.exists(test_manifest_path):
        os.remove(test_manifest_path)
