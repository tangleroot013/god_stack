# ==============================================================================
# STRUCTURED STORAGE INTERFACE LAYER WITH QUEUE ENGINE (matrix_storage.py)
# Architecture: Standard Library sqlite3 with Async Thread Job Queue Pools
# ==============================================================================
import sqlite3
import asyncio
import logging
from datetime import datetime, timezone

logging.basicConfig(
    level=logging.INFO, 
    format="\033[1;33m%(asctime)s\033[0m | \033[1;32m[STORAGE-CORE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixStorage")

class MatrixStorage:
    def __init__(self, db_path: str = "matrix_vault.db"):
        self.db_path = db_path

    def _sync_initialize(self):
        """Prepares the scraped payloads cache and long-running job queue tables."""
        with sqlite3.connect(self.db_path) as db:
            # 1. Scraped outputs table
            db.execute("""
                CREATE TABLE IF NOT EXISTS scraped_payloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_url TEXT NOT NULL,
                    page_title TEXT,
                    raw_markdown TEXT,
                    data_density_bytes INTEGER,
                    egress_proxy TEXT,
                    captured_at TEXT NOT NULL
                );
            """)
            db.execute("CREATE INDEX IF NOT EXISTS idx_target_url ON scraped_payloads (target_url);")
            
            # 2. Continuous Daemon Job queue table
            db.execute("""
                CREATE TABLE IF NOT EXISTS crawl_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_url TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
                    last_attempt TEXT,
                    retry_count INTEGER DEFAULT 0
                );
            """)
            db.commit()

    def _sync_commit(self, url: str, title: str, markdown: str, proxy: str, timestamp: str, density: int) -> int:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute("""
                INSERT INTO scraped_payloads (
                    target_url, page_title, raw_markdown, data_density_bytes, egress_proxy, captured_at
                ) VALUES (?, ?, ?, ?, ?, ?);
            """, (url, title, markdown, density, proxy or "CLEAR_NET", timestamp))
            db.commit()
            return cursor.lastrowid

    def _sync_seed_jobs(self, urls: list):
        """Ensures targets exist within the daemon operational table without duplicates."""
        with sqlite3.connect(self.db_path) as db:
            for url in urls:
                db.execute("INSERT OR IGNORE INTO crawl_jobs (target_url) VALUES (?);", (url,))
            db.commit()

    def _sync_fetch_next_job(self):
        """Claims and returns the next pending item, flipping its status instantly."""
        with sqlite3.connect(self.db_path) as db:
            db.row_factory = sqlite3.Row
            cursor = db.execute("SELECT * FROM crawl_jobs WHERE status = 'PENDING' LIMIT 1;")
            row = cursor.fetchone()
            if row:
                db.execute("UPDATE crawl_jobs SET status = 'PROCESSING' WHERE id = ?;", (row["id"],))
                db.commit()
                return dict(row)
            return None

    def _sync_update_job_status(self, job_id: int, status: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as db:
            db.execute("""
                UPDATE crawl_jobs 
                SET status = ?, last_attempt = ?, retry_count = retry_count + 1 
                WHERE id = ?;
            """, (status, timestamp, job_id))
            db.commit()

    async def initialize_vault(self):
        await asyncio.to_thread(self._sync_initialize)
        logger.info(f"Relational storage initialized successfully at: {self.db_path}")

    async def seed_job_matrix(self, urls: list):
        await asyncio.to_thread(self._sync_seed_jobs, urls)

    async def fetch_next_job(self):
        return await asyncio.to_thread(self._sync_fetch_next_job)

    async def update_job_status(self, job_id: int, status: str):
        await asyncio.to_thread(self._sync_update_job_status, job_id, status)

    async def commit_payload(self, url: str, title: str, markdown: str, proxy: str) -> int:
        timestamp = datetime.now(timezone.utc).isoformat()
        density = len(markdown.encode('utf-8')) if markdown else 0
        row_id = await asyncio.to_thread(self._sync_commit, url, title, markdown, proxy, timestamp, density)
        logger.info(f"Payload transaction secured. Primary Key ID: [ {row_id} ] ({density} bytes encoded)")
        return row_id

    def _sync_check_url_exists(self, url: str) -> bool:
        with sqlite3.connect(self.db_path) as db:
            cursor = db.execute(
                "SELECT 1 FROM crawl_jobs WHERE target_url = ? "
                "UNION SELECT 1 FROM scraped_payloads WHERE target_url = ? LIMIT 1;",
                (url, url)
            )
            return cursor.fetchone() is not None

    async def check_url_exists(self, url: str) -> bool:
        return await asyncio.to_thread(self._sync_check_url_exists, url)
