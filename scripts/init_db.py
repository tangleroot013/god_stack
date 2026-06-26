#!/usr/bin/env python3
import sqlite3
import pathlib

db_path = pathlib.Path('storage.sqlite')
migration_path = pathlib.Path('migrations/20260625_add_ingestion_records.sql')

print(f"[*] Initializing cluster schema on target: {db_path}...")
conn = sqlite3.connect(db_path)
try:
    with open(migration_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    print("[SUCCESS] Database schema initialized and locked.")
except Exception as e:
    print(f"[ERROR] Migration block failed: {str(e)}")
finally:
    conn.close()
