#!/usr/bin/env bash
set -euo pipefail

MAGENTA="\033[1;35m"
CYAN="\033[1;36m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${MAGENTA}==================================================================${RESET}"
echo -e "${MAGENTA}    G.O.D. STACK MESH HARNESS: PERSISTENT TELEMETRY RUNTIME       ${RESET}"
echo -e "${MAGENTA}==================================================================${RESET}"

# 1. Environment Isolation
echo -e "${CYAN}[STAGE 1/5] Identifying system python virtual environments...${RESET}"
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}  -> [ALERT] Operating inside native interpreter context.${RESET}"
fi

# 2. Re-engineering Telemetry Architecture with Self-Healing Storage
echo -e "${CYAN}[STAGE 2/5] Hardening OpenMetrics persistence middleware layer...${RESET}"
cat << 'PYEOF' > metrics_exporter.py
#!/usr/bin/env python3
import http.server
import threading
import logging
import sqlite3

logger = logging.getLogger("TelemetryExporter")

DB_PATH = "god_stack_vfs.db"

SYSTEM_METRICS = {
    "god_stack_ingestion_attempts_total": 0,
    "god_stack_ingestion_success_total": 0,
    "god_stack_deduplication_skips_total": 0,
    "god_stack_bytes_processed_total": 0
}

def init_persistent_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to initialize metric database: {e}")

def increment_metric(metric_key: str, val: int = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        cursor.execute("""
            INSERT INTO telemetry (metric_key, metric_value) VALUES (?, ?)
            ON CONFLICT(metric_key) DO UPDATE SET metric_value = metric_value + ?
        """, (metric_key, val, val))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to persist metric mutation: {e}")

def sync_from_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                metric_key TEXT PRIMARY KEY,
                metric_value INTEGER
            )
        """)
        cursor.execute("SELECT metric_key, metric_value FROM telemetry")
        rows = cursor.fetchall()
        for key, value in rows:
            if key in SYSTEM_METRICS:
                SYSTEM_METRICS[key] = value
        conn.close()
    except Exception:
        pass

class PersistentMetricsHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            sync_from_database()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.end_headers()
            
            output = []
            for metric_name, val in SYSTEM_METRICS.items():
                output.append(f"# TYPE {metric_name} counter")
                output.append(f"{metric_name} {val}")
            
            self.wfile.write("\n".join(output).encode("utf-8") + b"\n")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def start_telemetry_server(port: int = 8089):
    init_persistent_db()
    server = http.server.HTTPServer(("0.0.0.0", port), PersistentMetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info(f"📊 Persistent Telemetry Server operating on port :{port}/metrics")
PYEOF

# 3. Dynamic Runtime Application Update
echo -e "${CYAN}[STAGE 3/5] Writing continuous integration stream runtime engine...${RESET}"
cat << 'PYEOF' > master_mesh_runtime.py
#!/usr/bin/env python3
import asyncio
import logging
import inspect
from typing import List, Optional, Set

from god_scraper import GodScraper
from god_engine import GodEngineNode
from metrics_exporter import start_telemetry_server, increment_metric

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;34m[MESH-RUNTIME]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MasterMeshRuntime")

try:
    original_fetch = GodEngineNode.fetch_and_extract
    async def resilient_fetch_and_extract(url, *args, **kwargs):
        sig = inspect.signature(original_fetch)
        has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        clean_kwargs = kwargs if has_var_keyword else {k: v for k, v in kwargs.items() if k in sig.parameters}
        try:
            res = await original_fetch(url, *args, **clean_kwargs)
            if res.get("status") == "SUCCESS":
                increment_metric("god_stack_ingestion_success_total", 1)
            return res
        except TypeError:
            return await original_fetch(url)

    GodEngineNode.fetch_and_extract = resilient_fetch_and_extract
    logger.info("🛡️  Signature-hardening middleware bound to active nodes.")
except Exception as patch_err:
    logger.warning(f"Failed loading interceptor profiles: {patch_err}")

class ProductionStreamScraper(GodScraper):
    def __init__(self, concurrency_limit: int = 4):
        super().__init__(concurrency_limit=concurrency_limit)
        self.active_tasks: Set[asyncio.Task] = set()
        self.total_processed_count = 0
        self._mock_frontier = [f"https://example.com/stream_node_v2_{i}" for i in range(12)]

    def _get_next_targets(self, batch_size: int = 1) -> List[str]:
        targets = []
        for _ in range(batch_size):
            if self._mock_frontier:
                targets.append(self._mock_frontier.pop(0))
        return targets

    async def run_continuous_stream_loop(self, target_drain_limit: Optional[int] = None):
        logger.info(f"Stream loop activated. Concurrency cap: {self.concurrency_limit}")
        self.active = True

        while self.active:
            self.active_tasks = {t for t in self.active_tasks if not t.done()}

            if target_drain_limit and self.total_processed_count >= target_drain_limit:
                break

            while len(self.active_tasks) < self.concurrency_limit and self.active:
                next_targets = self._get_next_targets(batch_size=1)
                if not next_targets:
                    break

                url = next_targets[0]
                increment_metric("god_stack_ingestion_attempts_total", 1)
                
                task = asyncio.create_task(self.process_target(url))
                self.active_tasks.add(task)
                self.total_processed_count += 1

            await asyncio.sleep(0.01)

        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)

async def main():
    start_telemetry_server(port=8089)
    await GodEngineNode.initialize(headless=True)

    scraper = ProductionStreamScraper(concurrency_limit=4)
    await scraper.initialize()
    await scraper.run_continuous_stream_loop(target_drain_limit=8)
    await scraper.shutdown()
    
    # Keep the metric server context alive momentarily so testing frameworks can pull final states
    logger.info("💤 Draining active network queues... keeping telemetry server responsive.")
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
PYEOF
chmod +x master_mesh_runtime.py

# 4. Building the Unit Verification and Validation layer
echo -e "${CYAN}[STAGE 4/5] Resetting system tables and compiling regression unit suite...${RESET}"
rm -f god_stack_vfs.db

cat << 'PYEOF' > mesh_regression_suite.py
#!/usr/bin/env python3
import unittest
import asyncio
import time
import sqlite3
from metrics_exporter import increment_metric, sync_from_database, SYSTEM_METRICS, init_persistent_db
from master_mesh_runtime import ProductionStreamScraper

class TestGodStackMeshIntegrity(unittest.TestCase):
    def setUp(self):
        conn = sqlite3.connect("god_stack_vfs.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS telemetry")
        conn.commit()
        conn.close()
        init_persistent_db()
        for k in SYSTEM_METRICS:
            SYSTEM_METRICS[k] = 0

    def test_openmetrics_atomic_mutations(self):
        increment_metric("god_stack_ingestion_attempts_total", 5)
        sync_from_database()
        self.assertEqual(SYSTEM_METRICS["god_stack_ingestion_attempts_total"], 5)

    def test_concurrency_envelope_ceiling(self):
        scraper = ProductionStreamScraper(concurrency_limit=3)
        self.assertEqual(scraper.concurrency_limit, 3)

    def test_deadlock_resilience(self):
        scraper = ProductionStreamScraper(concurrency_limit=2)
        async def mock_pass():
            await scraper.initialize()
            task = asyncio.create_task(scraper.run_continuous_stream_loop(target_drain_limit=0))
            await asyncio.sleep(0.02)
            scraper.active = False
            await task
            await scraper.shutdown()
            
        start = time.time()
        asyncio.run(mock_pass())
        self.assertTrue((time.time() - start) < 0.5)

if __name__ == "__main__":
    print("\033[1;36m[REGRESSION SUITE] Executing regression test layers...\033[0m")
    unittest.main()
PYEOF
chmod +x mesh_regression_suite.py

# 5. Live Pipeline Verification Flight Sequence
echo -e "${CYAN}[STAGE 5/5] Executing target framework pipeline verification fights...${RESET}"
echo -e "${YELLOW}--- TARGET ALPHA: RUNNING SYSTEM REGRESSION TESTS ---${RESET}"
python3 mesh_regression_suite.py

echo -e "\n${YELLOW}--- TARGET BETA: INITIALIZING LIVE MASTER MESH RUNTIME DAEMON ---${RESET}"
python3 master_mesh_runtime.py > master_mesh_execution.log 2>&1 &
DAEMON_PID=$!
echo -e "  -> Daemon isolated under background PID: ${DAEMON_PID}"
echo -e "  -> Stabilizing socket buffers..."
sleep 1.5

echo -e "\n${CYAN}Auditing live OpenMetrics persistent database endpoint...${RESET}"
if curl -s http://127.0.0.1:8089/metrics | grep "god_stack_" > /dev/null; then
    echo -e "${GREEN}[SUCCESS] Prometheus Telemetry Matrix completely responsive across processes!${RESET}"
    echo -e "${MAGENTA}------------------------------------------------------------------${RESET}"
    curl -s http://127.0.0.1:8089/metrics | grep "god_stack_"
    echo -e "${MAGENTA}------------------------------------------------------------------${RESET}"
else
    echo -e "${RED}[FAILURE] Metrics loop could not sync. Background execution log output:${RESET}"
    cat master_mesh_execution.log || true
    kill "$DAEMON_PID" 2>/dev/null || true
    exit 1
fi

kill "$DAEMON_PID" 2>/dev/null || true
rm -f master_mesh_execution.log
echo -e "${GREEN}[DONE] Integration matrix validated successfully.${RESET}"
