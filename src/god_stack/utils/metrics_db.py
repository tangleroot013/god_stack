# ==============================================================================
# utils/metrics_db.py – Complete SQLite Telemetry Layer
# ==============================================================================
import sqlite3

DB_PATH = "storage.sqlite"

def _exec(sql, params=()):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(sql, params)
        conn.commit()

def init_schema():
    schema = """
    CREATE TABLE IF NOT EXISTS worker_executions (
        ts INTEGER NOT NULL,
        worker_name TEXT NOT NULL,
        status TEXT NOT NULL,
        count INTEGER NOT NULL,
        PRIMARY KEY (ts, worker_name, status)
    );
    CREATE TABLE IF NOT EXISTS daemon_loop (
        ts INTEGER NOT NULL,
        duration REAL NOT NULL,
        memory_bytes REAL NOT NULL
    );
    """
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(schema)

def record_worker(name, status):
    _exec(
        """
        INSERT INTO worker_executions (ts, worker_name, status, count)
        VALUES (strftime('%s','now'), ?, ?, 1)
        ON CONFLICT(ts, worker_name, status) DO UPDATE SET count = count + 1;
        """,
        (name, status),
    )

# Auto-initialize schema upon module import
init_schema()
