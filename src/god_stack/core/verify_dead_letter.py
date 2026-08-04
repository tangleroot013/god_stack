#!/usr/bin/env python3
import json
import pathlib
import sys

# Matched directly to the active DeadLetterStream output matrix
REQUIRED_FIELDS = {"url", "timestamp", "error"}

def validate_line(line: str, lineno: int) -> bool:
    try:
        record = json.loads(line)
    except json.JSONDecodeError as exc:
        print(f"[❌] Line {lineno}: invalid JSON – {exc}", file=sys.stderr)
        return False

    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        print(f"[❌] Line {lineno}: missing fields {sorted(missing)}", file=sys.stderr)
        return False

    if not isinstance(record["url"], str):
        print(f"[❌] Line {lineno}: url should be a string", file=sys.stderr)
        return False
    if not isinstance(record["timestamp"], str):
        print(f"[❌] Line {lineno}: timestamp should be an ISO-8601 string", file=sys.stderr)
        return False
    if not isinstance(record["error"], str):
        print(f"[❌] Line {lineno}: error context should be a string", file=sys.stderr)
        return False

    return True

def main():
    dead_letter_path = pathlib.Path("outputs/dead_letter_vault.jsonl")
    if not dead_letter_path.is_file():
        print("[⚠️] dead_letter_vault.jsonl not found – skipping validation", file=sys.stderr)
        sys.exit(0)

    all_ok = True
    with dead_letter_path.open() as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:  
                continue
            if not validate_line(line, i):
                all_ok = False

    if all_ok:
        print("[✅] dead_letter_vault.jsonl passed all engine structural checks")
    else:
        print("[❗] Validation failed – structural anomalies detected", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
