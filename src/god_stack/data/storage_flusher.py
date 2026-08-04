#!/usr/bin/env python3
import asyncio
import sqlite3
import logging
from typing import List, Dict, Any

logger = logging.getLogger("GodStack.StorageFlusher")

class StorageFlusher:
    def __init__(self, db_path: str, batch_size: int = 50, flush_interval_seconds: float = 5.0):
        self.db_path = db_path
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        self.queue = asyncio.Queue()
        self._is_running = False
        self._worker_task = None

    async def start(self):
        if not self._is_running:
            self._is_running = True
            self._worker_task = asyncio.create_task(self._periodic_flush_loop())

    async def enqueue_payload(self, source_domain: str, target_url: str, title: str, summary: str, status: str):
        await self.queue.put({
            "domain": source_domain, "url": target_url, "title": title, "summary": summary, "status": status
        })

    async def _periodic_flush_loop(self):
        while self._is_running:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                await self.flush_records()
            except asyncio.CancelledError:
                break

    async def flush_records(self):
        if self.queue.empty(): return
        records = []
        while not self.queue.empty() and len(records) < self.batch_size:
            records.append(await self.queue.get())
        if not records: return
        await asyncio.to_thread(self._execute_batch_insert, records)

    def _execute_batch_insert(self, records: List[Dict[Any, Any]]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingestion_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_domain TEXT, target_url TEXT, title TEXT, summary TEXT, status TEXT
            )
        """)
        payload_tuples = [(r["domain"], r["url"], r["title"], r["summary"], r["status"]) for r in records]
        cursor.executemany("INSERT INTO ingestion_ledger (source_domain, target_url, title, summary, status) VALUES (?, ?, ?, ?, ?)", payload_tuples)
        conn.commit()
        conn.close()

    async def stop(self):
        self._is_running = False
        if self._worker_task:
            self._worker_task.cancel()
            try: await self._worker_task
            except asyncio.CancelledError: pass
        await self.flush_records()
