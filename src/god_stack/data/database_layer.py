#!/usr/bin/env python3
import sqlite3
from queue import Queue
from pathlib import Path
import threading
import atexit

class SQLitePool:
    """Thread-safe SQLite connection pool with WAL mode for crash recovery."""
    
    def __init__(self, db_path="storage.sqlite", pool_size=5):
        self.db_path = Path(db_path)
        self.pool = Queue(maxsize=pool_size)
        self.lock = threading.Lock()
        
        # Initialize schema on first run
        self._init_schema()
        
        # Pre-populate pool with connections
        for _ in range(pool_size):
            conn = self._create_connection()
            self.pool.put(conn)
        
        # Ensure cleanup on exit
        atexit.register(self.close_all)
    
    def _create_connection(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for crash safety
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance safety & speed
        return conn
    
    def _init_schema(self):
        """Create research_ledger table if it doesn't exist."""
        conn = self._create_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_domain TEXT NOT NULL,
                target_url TEXT UNIQUE NOT NULL,
                research_title TEXT,
                extracted_text_summary TEXT,
                status TEXT CHECK(status IN ('SUCCESS', 'QUARANTINED', 'RETRY')),
                error_type TEXT,
                worker_id TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status ON research_ledger(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_domain ON research_ledger(source_domain)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_url ON research_ledger(target_url)
        """)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get a connection from the pool (blocks if empty)."""
        return self.pool.get()
    
    def return_connection(self, conn):
        """Return a connection to the pool."""
        self.pool.put(conn)
    
    def close_all(self):
        """Graceful shutdown: close all pooled connections."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except:
                pass

class ResearchLedger:
    """Database abstraction for research records."""
    
    def __init__(self, pool):
        self.pool = pool
    
    def insert_record(self, row_data):
        """Thread-safe insert with deduplication (INSERT OR IGNORE)."""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO research_ledger
                (source_domain, target_url, research_title, extracted_text_summary, status, error_type, worker_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row_data.get("Source_Domain"),
                row_data.get("Target_URL"),
                row_data.get("Research_Title"),
                row_data.get("Extracted_Text_Summary"),
                row_data.get("Status"),
                row_data.get("Error_Type"),
                row_data.get("Worker_ID")
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            self.pool.return_connection(conn)
    
    def get_metrics(self):
        """Query live pipeline metrics."""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM research_ledger WHERE status = 'SUCCESS'")
            success_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM research_ledger WHERE status = 'QUARANTINED'")
            quarantined_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM research_ledger")
            total_count = cursor.fetchone()[0]
            
            return {
                "total": total_count,
                "success": success_count,
                "quarantined": quarantined_count
            }
        finally:
            self.pool.return_connection(conn)
    
    def get_last_processed_id(self):
        """For resumability: get the highest ID successfully processed."""
        conn = self.pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(id) FROM research_ledger WHERE status = 'SUCCESS'")
            result = cursor.fetchone()[0]
            return result if result else 0
        finally:
            self.pool.return_connection(conn)

if __name__ == "__main__":
    # Quick validation
    pool = SQLitePool()
    ledger = ResearchLedger(pool)
    
    # Test insert
    ledger.insert_record({
        "Source_Domain": "test.example.com",
        "Target_URL": "https://test.example.com/page",
        "Research_Title": "Test Record",
        "Extracted_Text_Summary": "This is a test",
        "Status": "SUCCESS",
        "Error_Type": None,
        "Worker_ID": "test_worker"
    })
    
    metrics = ledger.get_metrics()
    print(f"[✅] Database initialized. Metrics: {metrics}")
