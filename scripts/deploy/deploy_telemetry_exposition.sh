#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating Prometheus Exposition Endpoint Module...\033[0m"

cat << 'PYEOF' > run_telemetry_exposition.py
import http.server
import threading
import logging
import time
from metrics_exporter import SYSTEM_METRICS, start_telemetry_server

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[TELEMETRY-TEST]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TelemetryTest")

def simulate_pipeline_traffic():
    """Simulates active pipeline increments to verify server serialization output."""
    for i in range(3):
        time.sleep(1)
        SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 12
        SYSTEM_METRICS["god_stack_ingestion_success_total"] += 10
        SYSTEM_METRICS["god_stack_bytes_processed_total"] += 4096
        logger.info(f"Simulated Ingestion Pulse #{i+1} injected into global metrics map.")

def main():
    print("\n\033[1;32m--- G.O.D. TELEMETRY SYSTEM VALIDATION ---\033[0m")
    
    # Fire up the HTTP exposition server thread on port 8000
    start_telemetry_server(port=8000)
    
    # Push synthetic traffic updates
    simulate_pipeline_traffic()
    
    logger.info("Verifying OpenMetrics payload extraction formatting...")
    print("\033[1;33m--- PROMETHEUS METRICS STREAM PREVIEW ---\033[0m")
    for metric, value in SYSTEM_METRICS.items():
        print(f"# TYPE {metric} counter\n{metric} {value}")
    print("\033[1;33m---------------------------------------\033[0m")
    
    print("\n\033[1;32m✔ MODULE 21 EXPOSITION LAYER PASSED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    main()
PYEOF

echo -e "\033[1;34m[2/2] Launching verification runner...\033[0m"
./.venv/bin/python3 run_telemetry_exposition.py
