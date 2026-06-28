#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STORAGE SYNC ENGINE (data_storage_sync.py)
# Architecture: FOSS transactional deduplication and WAL schema manager.
# ==============================================================================
import os
import sqlite3
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger("StorageSync")

class StorageSyncEngine:
    def __init__(self, db_path: str = "storage.sqlite"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Forces WAL compilation target schemas on startup."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enforce high-concurrency Write-Ahead Logging
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Create core metrics tracking matrix table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_matrix (
                payload_hash TEXT PRIMARY KEY,
                title TEXT,
                source_url TEXT,
                extracted_at TEXT,
                content_length INTEGER,
                payload_data TEXT,
                status TEXT
            );
        """)
        conn.commit()
        conn.close()

    def calculate_fingerprint(self, source_url: str, title: str) -> str:
        """Generates an atomic SHA-256 key to maintain structural idempotency."""
        token_string = f"{source_url}::{title}"
        return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

    def sync_record(self, record: dict) -> bool:
        """Commits record to storage matrix layer or drops it if a duplicate is found."""
        payload_hash = self.calculate_fingerprint(record["source_url"], record["title"])
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ingestion_matrix 
                (payload_hash, title, source_url, extracted_at, content_length, payload_data, status)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                payload_hash,
                record["title"],
                record["source_url"],
                record["extracted_at"],
                record["content_length"],
                record["payload_data"],
                record["status"]
            ))
            conn.commit()
            logger.info(f"💾 [STORAGE] Safely committed hash node: {payload_hash[:12]}... -> {record['title']}")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"🛡️ [DEDUPLICATION] Dropped duplicate footprint frame: {payload_hash[:12]}... (Skipped)")
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
    # Structural functional evaluation loop
    engine = StorageSyncEngine()
    test_node = {
        "title": "Diagnostic Feed Spec",
        "source_url": "https://example.com/spec",
        "extracted_at": datetime.utcnow().isoformat(),
        "content_length": 42,
        "payload_data": "Raw matrix stream validation elements.",
        "status": "PROCESSED"
    }
    engine.sync_record(test_node)
    # Attempt second insertion to verify the FOSS deduplication interceptor works
    engine.sync_record(test_node)
