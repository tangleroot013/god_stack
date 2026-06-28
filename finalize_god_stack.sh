#!/usr/bin/env bash
# ==============================================================================
# G.O.D. STACK INTERFERENCE IMMUNIZATION SMOKE TESTER (finalize_god_stack.sh)
# ==============================================================================
set -euo pipefail

BLUE="\033[1;34m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo -e "${BLUE}>>> Starting One-Click Live Verification Flow <<<${RESET}"

# 1. Acquire free dynamic socket identifier port
PORT=$(python3 -c 'import socket; s=socket.socket(); s.bind(("0.0.0.0", 0)); print(s.getsockname()[1]); s.close()')

# 2. Run background telemetry daemon
python3 -c "import metrics_exporter; metrics_exporter.start_telemetry_server(port=$PORT)" &
EXP_PID=$!
trap 'kill $EXP_PID 2>/dev/null || true' EXIT

sleep 1

# 3. Simulate targeted single execution through unblocking engine loops
python3 - << 'PY_EOF'
import asyncio
from god_scraper import GodScraper
from metrics_exporter import SYSTEM_METRICS

async def main():
    scraper = GodScraper(concurrency_limit=2, profile_name="review_hardening_demo")
    await scraper.initialize(headless=True)
    await scraper.process_target("https://example.com")
    await scraper.shutdown()

asyncio.run(main())
PY_EOF

# 4. Check exposed values matches standard metric open format specifications
if curl -s "http://127.0.0.1:${PORT}/metrics" | grep -q "god_stack_ingestion_attempts_total"; then
    print "\n\033[1;32m✅ Smoke Test Passed — Telemetry, Sandbox Engine and Profiles Integrated Successfully.\033[0m\n"
else
    print "\n\033[1;31m❌ Verification Failure — Metric pathing error caught.\033[0m\n"
    exit 1
fi
