#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Engineering Structured CSV Batch Target Operator...\033[0m"

cat << 'PYEOF' > csv_operator.py
import csv
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[CSV-OP]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CSVOperator")

class CSVDataOperator:
    def export_telemetry_results(self, filepath: str, results_matrix: list):
        print("\n\033[1;32m--- G.O.D. CSV DATA EXPORT MATRIX ---\033[0m")
        if not results_matrix:
            logger.warning("Empty result matrix provided. Bypassing CSV write operations.")
            return

        keys = results_matrix[0].keys()
        with open(filepath, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results_matrix)
            
        logger.info(f"Successfully flushed \033[1;33m{len(results_matrix)}\033[0m payload records to FOSS-compliant CSV: [ {filepath} ]")

    def import_target_urls(self, filepath: str) -> list:
        print("\n\033[1;32m--- G.O.D. CSV TARGET INGESTION ---\033[0m")
        if not os.path.exists(filepath):
            logger.error(f"Target file [ {filepath} ] unmapped. Aborting ingestion.")
            return []

        targets = []
        with open(filepath, 'r', newline='') as input_file:
            csv_reader = csv.reader(input_file)
            for row in csv_reader:
                if row:  # Bypass blank indices
                    targets.append(row[0])
                    
        logger.info(f"Ingested \033[1;34m{len(targets)}\033[0m target URLs into active volatile memory.")
        return targets

if __name__ == "__main__":
    operator = CSVDataOperator()
    
    # Simulate Export
    sample_data = [{"url": "http://node-alpha.internal", "status": "200", "latency": "45ms"}]
    operator.export_telemetry_results("storage/export_test.csv", sample_data)
    
    # Simulate Import
    operator.import_target_urls("storage/export_test.csv")
    print("\n\033[1;32m✔ MODULE 105 CSV INGEST/EXPORT ENGINE SECURED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Validating row mapping and serialization loops...\033[0m"
chmod +x csv_operator.py
./.venv/bin/python3 csv_operator.py
