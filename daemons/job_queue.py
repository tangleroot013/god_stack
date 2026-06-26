import sqlite3
import logging
import os

class DistributedTaskQueue:
    """A centralized FIFO broker for multi-worker synchronization."""
    def __init__(self, db_path="/home/tangleroot013/god_stack/outputs/task_matrix.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_broker()

    def _initialize_broker(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    status TEXT DEFAULT 'pending',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_target(self, url: str):
        """Injects a new target into the global task matrix."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO queue (url) VALUES (?)", (url,))
        except sqlite3.IntegrityError:
            pass # Target already exists in the matrix

    def pop_task(self) -> str:
        """Atomically retrieves the next pending task and marks it as active."""
        with sqlite3.connect(self.db_path, timeout=30.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute("SELECT id, url FROM queue WHERE status = 'pending' LIMIT 1")
            task = cursor.fetchone()
            if task:
                cursor.execute("UPDATE queue SET status = 'active' WHERE id = ?", (task['id'],))
                conn.commit()
                return task['url']
            conn.commit()
        return None
