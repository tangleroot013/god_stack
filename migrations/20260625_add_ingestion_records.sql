CREATE TABLE IF NOT EXISTS vault_index (
    sha256 TEXT PRIMARY KEY,
    source_url TEXT NOT NULL,
    run_id TEXT NOT NULL,
    stored_at TEXT NOT NULL,
    vault_path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    run_id TEXT NOT NULL,
    status TEXT NOT NULL,
    details TEXT
);
