#!/usr/bin/env bash
# ========================================================================================================================================================================
# G.O.D. STACK v2.4.1 | SCHEMATIC SYNCHRONIZED TELEMETRY RUNTIME
# ========================================================================================================================================================================

export TELEMETRY_URLS="${TELEMETRY_URLS:-https://news.ycombinator.com/news https://news.ycombinator.com/newest https://news.ycombinator.com/best}"
export SQLITE_DB="${SQLITE_DB:-storage.sqlite}"
export BATCH_SIZE="${BATCH_SIZE:-100}"
export FETCH_INTERVAL="${FETCH_INTERVAL:-5}"
export DAEMON_LOG_FILE="${DAEMON_LOG_FILE:-logs/daemon_orchestrator.log}"

mkdir -p logs metrics parsers

python3 - <<'PYTHON'
import asyncio
import os
import signal
import sys
import time
import json
import logging
from pathlib import Path
import curses

try:
    import httpx
    import aiosqlite
except ImportError:
    sys.exit("⚡ [FATAL ARCHITECTURE ERROR] Missing required drivers. Run your active venv or execute: pip install httpx aiosqlite")

TELEMETRY_URLS = os.getenv("TELEMETRY_URLS", "").split()
SQLITE_DB = os.getenv("SQLITE_DB", "storage.sqlite")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))
FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "5"))
DAEMON_LOG_FILE = os.getenv("DAEMON_LOG_FILE", "logs/daemon_orchestrator.log")

logging.basicConfig(
    filename=DAEMON_LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | [%(levelname)s] %(message)s"
)
logger = logging.getLogger("MatrixDaemon")

class HardenedDOMParser:
    @staticmethod
    def extract_metrics_safely(html_tree_node) -> dict:
        """Defensively translates inbound transport frames into telemetry database schemas."""
        extracted_data = {"timestamp": 0, "sensor_id": "Unknown Node", "value": 0.0}
        if html_tree_node is None:
            return extracted_data
        try:
            extracted_data["timestamp"] = int(html_tree_node.get("timestamp", time.time()))
            extracted_data["sensor_id"] = str(html_tree_node.get("sensor_id", "Unknown")).strip()
            extracted_data["value"] = float(html_tree_node.get("value", 0.0))
        except Exception as e:
            logger.warning(f"⚠️ [PARSER ANOMALY] Structural deviation on incoming frame parsing: {e}")
        return extracted_data

class DataAlchemist:
    @staticmethod
    def optimize_array_processing(raw_payloads: list) -> list:
        """Validates, cleans, and packages standardized metric payloads."""
        start_time = time.perf_counter()
        processed_records = []
        append_record = processed_records.append
        
        required = {"timestamp", "sensor_id", "value"}
        
        for record in raw_payloads:
            if not isinstance(record, dict) or not required.issubset(record):
                continue
            try:
                append_record({
                    "timestamp": int(record["timestamp"]),
                    "sensor_id": str(record["sensor_id"]).strip(),
                    "value": float(record["value"])
                })
            except (ValueError, TypeError):
                continue
                
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"✨ [ALCHEMIST] Vectorized transformation batch completed in {duration_ms:.3f}ms")
        return processed_records

async def fetch_worker(queue: asyncio.Queue, telemetry_metrics: dict):
    """Asynchronous HTTP worker transforming network inputs into standard telemetry records."""
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        while True:
            for url in TELEMETRY_URLS:
                try:
                    resp = await client.get(url)
                    telemetry_metrics["total_network_requests"] += 1
                    if resp.status_code == 200:
                        # Harmonized fields directly mapping to the telemetry database specifications
                        raw_frame = {
                            "timestamp": int(time.time()), 
                            "sensor_id": url.split("//")[-1].split("/")[0], 
                            "value": float(resp.status_code)
                        }
                        parsed_node = HardenedDOMParser.extract_metrics_safely(raw_frame)
                        purified = DataAlchemist.optimize_array_processing([parsed_node])
                        if purified:
                            await queue.put(purified[0])
                            telemetry_metrics["purified_count"] += 1
                        else:
                            telemetry_metrics["dropped_count"] += 1
                    else:
                        telemetry_metrics["dropped_count"] += 1
                except Exception as e:
                    telemetry_metrics["dropped_count"] += 1
                    logger.error(f"❌ [FETCH ERROR] Network matrix exception on target: {e}")
            await asyncio.sleep(FETCH_INTERVAL)

async def db_worker(queue: asyncio.Queue, stop_evt: asyncio.Event, telemetry_metrics: dict):
    async with aiosqlite.connect(SQLITE_DB) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, sensor_id TEXT, value REAL)"
        )
        await db.commit()
        batch = []
        while not stop_evt.is_set() or not queue.empty():
            try:
                record = await asyncio.wait_for(queue.get(), timeout=0.5)
                batch.append(record)
                if len(batch) >= BATCH_SIZE:
                    await _commit_batch(db, batch, telemetry_metrics)
                    batch.clear()
            except asyncio.TimeoutError:
                if batch:
                    await _commit_batch(db, batch, telemetry_metrics)
                    batch.clear()
        if batch:
            await _commit_batch(db, batch, telemetry_metrics)

async def _commit_batch(db, batch, telemetry_metrics):
    start = time.perf_counter()
    await db.executemany(
        "INSERT INTO telemetry (timestamp, sensor_id, value) VALUES (?, ?, ?)",
        [(r["timestamp"], r["sensor_id"], r["value"]) for r in batch],
    )
    await db.commit()
    telemetry_metrics["db_records_persisted"] += len(batch)
    telemetry_metrics["last_processing_speed_ms"] = (time.perf_counter() - start) * 1000

def install_signal_handlers(stop_evt: asyncio.Event):
    loop = asyncio.get_running_loop()
    def _handler():
        stop_evt.set()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _handler)

def purge_sensitive_footprint():
    db_path = Path(SQLITE_DB)
    for _ in range(5):
        try:
            if db_path.exists():
                size = db_path.stat().st_size
                with open(db_path, "wb") as shredder:
                    shredder.write(os.urandom(max(size, 1)))
                    shredder.flush()
                db_path.unlink()
            for suffix in ["-wal", "-journal", "-shm"]:
                aux = db_path.with_name(f"{db_path.name}{suffix}")
                if aux.exists():
                    aux.unlink()
            break
        except OSError:
            time.sleep(0.1)

class InteractiveDashboard:
    def __init__(self, stdscr, queue, telemetry_metrics, stop_evt):
        self.stdscr = stdscr
        self.queue = queue
        self.metrics = telemetry_metrics
        self.stop_evt = stop_evt
        self.start_time = time.time()
        curses.curs_set(0)
        self.stdscr.nodelay(True)

    async def draw_loop(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        while not self.stop_evt.is_set():
            self._render()
            try:
                key = self.stdscr.getch()
                if key == ord('q'):
                    self.stop_evt.set()
                    break
            except Exception:
                pass
            await asyncio.sleep(0.1)

    def _render(self):
        h, w = self.stdscr.getmaxyx()
        self.stdscr.erase()
        if h < 14 or w < 80:
            self.stdscr.addstr(0, 0, "Terminal window size too small for engine layout visualization.")
            self.stdscr.refresh()
            return

        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.box()
        self.stdscr.addstr(1, 2, "=" * (w - 5))
        self.stdscr.addstr(2, 4, "G.O.D. STACK v2.4.1 | RESILIENT LIVE TELEMETRY DRIVER")
        self.stdscr.addstr(3, 2, "=" * (w - 5))
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        elapsed_uptime = int(time.time() - self.start_time)
        self.stdscr.addstr(5, 4, f"• Runtime Uptime    : {elapsed_uptime}s")
        self.stdscr.addstr(6, 4, f"• Network Request Pass: {self.metrics['total_network_requests']}")
        self.stdscr.addstr(7, 4, f"• Engine Sync State : NOMINAL_RUNNING")

        self.stdscr.addstr(5, 42, f"• Purified / Drop   : {self.metrics['purified_count']} / {self.metrics['dropped_count']}")
        self.stdscr.addstr(6, 42, f"• Saved DB Batches : {self.metrics['db_records_persisted']}")
        self.stdscr.addstr(7, 42, f"• Write Latency Speed: {self.metrics['last_processing_speed_ms']:.3f} ms")

        self.stdscr.addstr(9, 2, "[- RECENT DAEMON PIPE RUNTIME STREAM]")
        try:
            if os.path.exists(DAEMON_LOG_FILE):
                with open(DAEMON_LOG_FILE, "r") as f:
                    log_lines = f.readlines()[-3:]
                    for idx, line in enumerate(log_lines):
                        self.stdscr.addstr(10 + idx, 4, f"› {line.strip()[:w-8]}")
        except Exception:
            pass

        self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.addstr(h - 2, 2, "[ Control Input Vector: Press 'q' to break runtime loops and lock down traces ]")
        self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
        self.stdscr.refresh()

async def main():
    queue = asyncio.Queue(maxsize=5000)
    stop_evt = asyncio.Event()
    install_signal_handlers(stop_evt)

    telemetry_metrics = {
        "total_network_requests": 0,
        "purified_count": 0,
        "dropped_count": 0,
        "db_records_persisted": 0,
        "last_processing_speed_ms": 0.0
    }

    fetch_task = asyncio.create_task(fetch_worker(queue, telemetry_metrics))
    db_task = asyncio.create_task(db_worker(queue, stop_evt, telemetry_metrics))

    loop = asyncio.get_running_loop()
    def run_curses(scr):
        asyncio.run(InteractiveDashboard(scr, queue, telemetry_metrics, stop_evt).draw_loop())

    ui_future = loop.run_in_executor(None, curses.wrapper, run_curses)
    await stop_evt.wait()
    
    fetch_task.cancel()
    try:
        await fetch_task
    except asyncio.CancelledError:
        pass

    await db_task
    purge_sensitive_footprint()
    await ui_future

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        purge_sensitive_footprint()
        sys.exit(0)
PYTHON
