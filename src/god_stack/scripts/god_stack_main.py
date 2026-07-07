import asyncio
import os
import signal
import sys
import time
import logging
from pathlib import Path
import curses

try:
    import httpx
    import aiosqlite
except ImportError:
    sys.exit("⚡ [FATAL ARCHITECTURE ERROR] Missing drivers. Run your active venv or execute: pip install httpx aiosqlite")

TELEMETRY_URLS = os.getenv("TELEMETRY_URLS", "https://news.ycombinator.com/news https://news.ycombinator.com/newest https://news.ycombinator.com/best").split()
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
        extracted_data = {"timestamp": 0, "sensor_id": "Unknown Node", "value": 0.0}
        if html_tree_node is None:
            return extracted_data
        try:
            extracted_data["timestamp"] = int(html_tree_node.get("timestamp", time.time()))
            extracted_data["sensor_id"] = str(html_tree_node.get("sensor_id", "Unknown")).strip()
            extracted_data["value"] = float(html_tree_node.get("value", 0.0))
        except Exception as e:
            logger.warning(f"⚠️ [PARSER ANOMALY] Structural deviation: {e}")
        return extracted_data

class DataAlchemist:
    @staticmethod
    def optimize_array_processing(raw_payloads: list) -> list:
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
        logger.info(f"✨ [ALCHEMIST] Vectorized batch completed in {duration_ms:.3f}ms")
        return processed_records

async def fetch_worker(queue: asyncio.Queue, telemetry_metrics: dict, stop_evt: asyncio.Event):
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        while not stop_evt.is_set():
            for url in TELEMETRY_URLS:
                if stop_evt.is_set():
                    break
                try:
                    resp = await client.get(url)
                    telemetry_metrics["total_network_requests"] += 1
                    if resp.status_code == 200:
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
                    logger.error(f"❌ [FETCH ERROR] Network matrix exception: {e}")
            
            for _ in range(FETCH_INTERVAL * 20):
                if stop_evt.is_set():
                    break
                await asyncio.sleep(0.05)

async def db_worker(queue: asyncio.Queue, stop_evt: asyncio.Event, telemetry_metrics: dict):
    async with aiosqlite.connect(SQLITE_DB) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp INTEGER, sensor_id TEXT, value REAL)"
        )
        await db.commit()
        batch = []
        while not stop_evt.is_set() or not queue.empty():
            try:
                record = await asyncio.wait_for(queue.get(), timeout=0.05)
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
            time.sleep(0.05)

async def ui_loop(stdscr, telemetry_metrics: dict, stop_evt: asyncio.Event):
    start_time = time.time()
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.raw()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    while not stop_evt.is_set():
        h, w = stdscr.getmaxyx()
        stdscr.erase()
        if h < 14 or w < 80:
            stdscr.addstr(0, 0, "Terminal window size too small for engine layout.")
            stdscr.refresh()
        else:
            stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
            stdscr.box()
            stdscr.addstr(1, 2, "=" * (w - 5))
            stdscr.addstr(2, 4, "G.O.D. STACK v2.4.5 | RESILIENT LIVE TELEMETRY DRIVER")
            stdscr.addstr(3, 2, "=" * (w - 5))
            stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

            elapsed_uptime = int(time.time() - start_time)
            stdscr.addstr(5, 4, f"• Runtime Uptime    : {elapsed_uptime}s")
            stdscr.addstr(6, 4, f"• Network Request Pass: {telemetry_metrics['total_network_requests']}")
            stdscr.addstr(7, 4, f"• Engine Sync State : NOMINAL_RUNNING")

            stdscr.addstr(5, 42, f"• Purified / Drop   : {telemetry_metrics['purified_count']} / {telemetry_metrics['dropped_count']}")
            stdscr.addstr(6, 42, f"• Saved DB Batches : {telemetry_metrics['db_records_persisted']}")
            stdscr.addstr(7, 42, f"• Write Latency Speed: {telemetry_metrics['last_processing_speed_ms']:.3f} ms")

            stdscr.addstr(9, 2, "[- RECENT DAEMON PIPE RUNTIME STREAM]")
            try:
                if os.path.exists(DAEMON_LOG_FILE):
                    with open(DAEMON_LOG_FILE, "r") as f:
                        log_lines = f.readlines()[-3:]
                        for idx, line in enumerate(log_lines):
                            stdscr.addstr(10 + idx, 4, f"› {line.strip()[:w-8]}")
            except Exception:
                pass

            stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
            stdscr.addstr(h - 2, 2, "[ Control Input Vector: Press 'q' or 'Q' to break runtime loops gracefully ]")
            stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()

        try:
            key = stdscr.getch()
            if key in (ord('q'), ord('Q')):
                stop_evt.set()
                break
        except Exception:
            pass

        await asyncio.sleep(0.05)

async def main(stdscr):
    queue = asyncio.Queue(maxsize=5000)
    stop_evt = asyncio.Event()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: stop_evt.set())

    telemetry_metrics = {
        "total_network_requests": 0,
        "purified_count": 0,
        "dropped_count": 0,
        "db_records_persisted": 0,
        "last_processing_speed_ms": 0.0
    }

    fetch_task = asyncio.create_task(fetch_worker(queue, telemetry_metrics, stop_evt))
    db_task = asyncio.create_task(db_worker(queue, stop_evt, telemetry_metrics))
    ui_task = asyncio.create_task(ui_loop(stdscr, telemetry_metrics, stop_evt))

    await stop_evt.wait()
    logger.info("🛑 [DAEMON SHUTDOWN] Exit condition detected. Starting cleanup.")
    
    fetch_task.cancel()
    ui_task.cancel()
    await asyncio.gather(fetch_task, ui_task, return_exceptions=True)
    await db_task
    purge_sensitive_footprint()

if __name__ == "__main__":
    try:
        curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))
    except KeyboardInterrupt:
        purge_sensitive_footprint()
        sys.exit(0)
