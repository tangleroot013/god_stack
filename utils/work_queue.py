import sqlite3
import os
from typing import Optional, Tuple

class DistributedWorkQueue:
    def __init__(self, db_path: str = "/home/tangleroot013/god_stack/vaults/queue.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    status TEXT DEFAULT 'PENDING',
                    claimed_by TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def enqueue(self, url: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO queue (url) VALUES (?)", (url,))
                return True
        except sqlite3.IntegrityError:
            return False

    def lease_task(self, worker_id: str) -> Optional[Tuple[int, str]]:
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute("SELECT id, url FROM queue WHERE status = 'PENDING' ORDER BY id ASC LIMIT 1")
            row = cursor.fetchone()
            if row:
                task_id, url = row
                conn.execute(
                    "UPDATE queue SET status = 'PROCESSING', claimed_by = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (worker_id, task_id)
                )
                conn.commit()
                return task_id, url
            return None

    def complete_task(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE queue SET status = 'COMPLETED', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))

    def fail_task(self, task_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE queue SET status = 'PENDING', claimed_by = NULL, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
