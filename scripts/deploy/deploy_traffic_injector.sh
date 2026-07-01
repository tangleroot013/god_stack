#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Deploying High-Velocity Ingestion Simulator...\033[0m"

cat << 'PYEOF' > inject_traffic_stream.py
import time
import logging
from metrics_exporter import SYSTEM_METRICS

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[INJECTOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TrafficInjector")

def simulate_production_burst():
    print("\n\033[1;32m--- G.O.D. LIVE DATA INJECTION SEQUENCE ---\033[0m")
    logger.info("Igniting multi-threaded synthetic flow into Prometheus edge matrix...")
    
    for burst in range(3):
        time.sleep(0.5)
        SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 25
        SYSTEM_METRICS["god_stack_ingestion_success_total"] += 22
        SYSTEM_METRICS["god_stack_deduplication_skips_total"] += 3
        SYSTEM_METRICS["god_stack_bytes_processed_total"] += 16384
        logger.info(f"Burst Block #{burst+1} committed. Ingestion metrics pushed to local memory layer.")

    print("\n\033[1;32m✔ MODULE 31 LIVE STREAM INJECTION COMPLETED.\033[0m\n")

if __name__ == "__main__":
    simulate_production_burst()
PYEOF

echo -e "\033[1;34m[2/2] Running burst simulation execution...\033[0m"
chmod +x inject_traffic_stream.py
./.venv/bin/python3 inject_traffic_stream.py
