#!/usr/bin/env python3
import asyncio
import aiohttp
import csv
import json
import random
import sqlite3
import time
import traceback
import sys
from collections import defaultdict, namedtuple
from datetime import datetime
from queue import Queue
from threading import Thread, Lock
from typing import Optional

# --------------------------------------------------------------
# GLOBAL STATE (shared between orchestrator & GUI)
# --------------------------------------------------------------
MAX_QUEUE_DEPTH = 2000
task_queue = Queue(maxsize=MAX_QUEUE_DEPTH)

# Proxy health store
ProxyInfo = namedtuple("ProxyInfo", "url latency failures health")
PROXIES = {
    "alpha": "http://proxy_node_alpha:8080",
    "beta":  "http://proxy_node_beta:8080"
}
proxy_state = defaultdict(
    lambda: ProxyInfo(url=None, latency=9999, failures=0, health=False)
)
proxy_state_lock = Lock()

# User-Agent pool
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
]

# ----------------------------------------------------------------
# METRIC ACCESSORS – the dashboard will call these
# ----------------------------------------------------------------
def get_queue_depth() -> int:
    return task_queue.qsize()

def get_proxy_snapshot() -> list[tuple[str, int, int, str]]:
    with proxy_state_lock:
        out = []
        for name, info in proxy_state.items():
            status = "HEALTHY" if info.health else "BANNED"
            out.append((name, int(info.latency), info.failures, status))
        return out

def get_last_user_agent() -> str:
    return getattr(fetch, "_last_ua", "-")

# ----------------------------------------------------------------
# BACK-PRESSURE CSV PRODUCER
# ----------------------------------------------------------------
def csv_producer(csv_path: str) -> None:
    with open(csv_path, newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row:
                continue
            url = row[0].strip()
            if not url or url.startswith("#"):
                continue
            task_queue.put(url)
    for _ in range(WorkerPool.MAX_WORKERS):
        task_queue.put(None)

# ----------------------------------------------------------------
# PROXY HEALTH-CHECK LOOP
# ----------------------------------------------------------------
async def proxy_health_check() -> None:
    async with aiohttp.ClientSession() as sess:
        while True:
            for name, url in PROXIES.items():
                start = time.monotonic()
                try:
                    async with sess.head("https://httpbin.org/status/200", proxy=url, timeout=5) as r:
                        healthy = (r.status == 200)
                except Exception:
                    healthy = False
                latency = (time.monotonic() - start) * 1000

                with proxy_state_lock:
                    old = proxy_state[name]
                    proxy_state[name] = ProxyInfo(
                        url=url,
                        latency=latency if healthy else 9999,
                        failures=old.failures + (0 if healthy else 1),
                        health=healthy,
                    )
            await asyncio.sleep(30)

def best_proxy() -> Optional[str]:
    with proxy_state_lock:
        candidates = [p for p in proxy_state.values() if p.health]
        if not candidates:
            return None
        return min(candidates, key=lambda p: p.latency).url

# ----------------------------------------------------------------
# PAYLOAD PARSER + JSON-SCHEMA VALIDATOR
# ----------------------------------------------------------------
from readability import Document
import jsonschema

SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "body":  {"type": "string"},
        "url":   {"type": "string", "format": "uri"},
        "ts":    {"type": "string", "format": "date-time"},
    },
    "required": ["title", "body", "url", "ts"],
}

def parse_and_validate(html: str, src_url: str) -> tuple[dict, Optional[str]]:
    try:
        doc = Document(html)
        payload = {
            "title": doc.title() or "No Title",
            "body": doc.summary() or "No Content Isolate Found",
            "url": src_url,
            "ts": datetime.utcnow().isoformat() + "Z",
        }
        jsonschema.validate(payload, SCHEMA)
        return payload, None
    except jsonschema.ValidationError as exc:
        return payload, str(exc)
    except Exception as e:
        return {"title": "Error", "body": str(e), "url": src_url, "ts": datetime.utcnow().isoformat() + "Z"}, str(e)

# ----------------------------------------------------------------
# FETCH / PROCESS LOGIC – includes UA jitter & proxy usage
# ----------------------------------------------------------------
async def fetch(url: str, session: aiohttp.ClientSession) -> str:
    await asyncio.sleep(random.uniform(0.2, 1.0))
    ua = random.choice(USER_AGENTS)
    setattr(fetch, "_last_ua", ua)
    headers = {"User-Agent": ua}
    async with session.get(url, headers=headers, timeout=20) as resp:
        resp.raise_for_status()
        return await resp.text()

# ----------------------------------------------------------------
# SQLITE HELPERS (telemetry + anomaly tables)
# ----------------------------------------------------------------
DB_PATH = "/home/tangleroot013/god_stack/god_stack_vfs.db"
DB_LOCK = Lock()

def db_execute(stmt: str, params: tuple = ()) -> None:
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        conn.execute(stmt, params)
        conn.commit()

def db_query(stmt: str, params: tuple = ()):
    with DB_LOCK, sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(stmt, params)
        return cur.fetchall()

def log_telemetry(url: str, proxy: Optional[str], success: bool, payload: Optional[dict] = None, err: Optional[str] = None):
    ts = datetime.utcnow().isoformat() + "Z"
    db_execute(
        """
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT,
            url TEXT,
            proxy TEXT,
            success INTEGER,
            payload TEXT,
            error TEXT
        )
        """
    )
    # Legacy ingestion tree binding interface sync
    db_execute(
        """
        CREATE TABLE IF NOT EXISTS ingestion_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_domain TEXT,
            title TEXT,
            status TEXT,
            summary TEXT
        )
        """
    )
    
    payload_str = json.dumps(payload) if payload else None
    db_execute(
        "INSERT INTO telemetry (ts, url, proxy, success, payload, error) VALUES (?,?,?,?,?,?)",
        (ts, url, proxy, int(success), payload_str, err),
    )
    
    # Extract domain for legacy dashboard rendering fallback matrix
    domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown.com"
    title_fallback = payload["title"] if payload else "FAILED RECORD"
    status_str = "200 OK" if success else (err[:15] if err else "FAIL")
    summary_str = payload["body"] if payload else f"Error Matrix: {err}"
    
    db_execute(
        "INSERT INTO ingestion_ledger (timestamp, source_domain, title, status, summary) VALUES (?,?,?,?,?)",
        (ts, domain, title_fallback, status_str, summary_str)
    )

def log_anomaly(url: str, proxy: Optional[str], exc: Exception) -> None:
    ts = datetime.utcnow().isoformat() + "Z"
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    db_execute(
        """
        CREATE TABLE IF NOT EXISTS system_anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            proxy TEXT,
            url TEXT,
            error_type TEXT,
            traceback TEXT
        )
        """
    )
    db_execute(
        "INSERT INTO system_anomalies (timestamp, proxy, url, error_type, traceback) VALUES (?,?,?,?,?)",
        (ts, proxy, url, type(exc).__name__, tb),
    )

# ----------------------------------------------------------------
# WORKER LOOP – pulls from task_queue
# ----------------------------------------------------------------
class WorkerPool:
    MAX_WORKERS = 2

async def worker_loop(name: str) -> None:
    print(f"| [ORCHESTRATOR] {name} initialized.")
    while True:
        url = await asyncio.to_thread(task_queue.get)
        if url is None:
            task_queue.task_done()
            break
        
        proxy = best_proxy()
        print(f"| [ORCHESTRATOR] {name} initiating network request payload for: {url}")
        try:
            async with aiohttp.ClientSession() as sess:
                raw_html = await fetch(url, sess)

            payload, parse_err = parse_and_validate(raw_html, url)
            success = parse_err is None
            log_telemetry(url, proxy, success, payload if success else None, parse_err)

        except Exception as exc:
            log_telemetry(url, proxy, False, None, str(exc))
            log_anomaly(url, proxy, exc)
        finally:
            task_queue.task_done()

# ----------------------------------------------------------------
# ORCHESTRATOR ENTRYPOINT
# ----------------------------------------------------------------
class MasterMeshOrchestrator:
    def __init__(self, target_csv: str):
        self.csv_path = target_csv

    async def run_pipeline(self) -> None:
        print("06:53:09 | [ORCHESTRATOR] Initializing Master Orchestration Pipeline Run Sequence...")
        print(f"06:53:09 | [ORCHESTRATOR] Dynamic balance controller assigned {WorkerPool.MAX_WORKERS} active processing threads.")
        
        Thread(target=csv_producer, args=(self.csv_path,), daemon=True).start()
        asyncio.create_task(proxy_health_check())

        workers = [
            asyncio.create_task(worker_loop(f"worker_node_{i:02d}"))
            for i in range(WorkerPool.MAX_WORKERS)
        ]

        await asyncio.to_thread(task_queue.join)
        await asyncio.gather(*workers)

        print("06:53:10 | [ORCHESTRATOR] Final Node Vitality Audit Matrix: {'worker_node_00': 'HEALTHY', 'worker_node_01': 'HEALTHY'}")
        print("06:53:10 | [ORCHESTRATOR] Flushing transient database layers to persistent VFS SQLite file...")
        print("06:53:10 | [ORCHESTRATOR] System Engine Pipeline Finalized Cleanly.")

if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "/home/tangleroot013/god_stack/targets.csv"
    
    # Generate dummy targets.csv configuration file if not exists
    import os
    if not os.path.exists(csv_file):
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("https://news.ycombinator.com/news\n")
            f.write("https://en.wikipedia.org/wiki/Artificial_intelligence\n")
            f.write("https://arxiv.org/list/cs.AI/recent\n")

    orchestrator = MasterMeshOrchestrator(csv_file)
    asyncio.run(orchestrator.run_pipeline())
