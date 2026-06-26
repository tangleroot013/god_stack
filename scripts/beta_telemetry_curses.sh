#!/usr/bin/env bash
# ========================================================================================================================================================================
# G.O.D. STACK v2.4.5 | PRODUCTION ENV WRAPPER (VENV ALIGNED)
# ========================================================================================================================================================================

export TELEMETRY_URLS="${TELEMETRY_URLS:-https://news.ycombinator.com/news https://news.ycombinator.com/newest https://news.ycombinator.com/best}"
export SQLITE_DB="${SQLITE_DB:-storage.sqlite}"
export BATCH_SIZE="${BATCH_SIZE:-100}"
export FETCH_INTERVAL="${FETCH_INTERVAL:-5}"
export DAEMON_LOG_FILE="${DAEMON_LOG_FILE:-logs/daemon_orchestrator.log}"

mkdir -p logs metrics parsers

# Pin execution to your local virtual environment interpreter
if [ -f "./.venv/bin/python3" ]; then
    ./.venv/bin/python3 ./scripts/god_stack_main.py
elif [ -f "./venv/bin/python3" ]; then
    ./venv/bin/python3 ./scripts/god_stack_main.py
else
    # Fallback to system Python if no venv directory structure matches
    python3 ./scripts/god_stack_main.py
fi
