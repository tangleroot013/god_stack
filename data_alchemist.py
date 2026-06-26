# ==============================================================================
# G.O.D. STACK DATA ALCHEMIST v1.0.1 (data_alchemist.py)
# Architecture: Heterogeneous Payload Aggregation & Clean CSV Transmutation
# ==============================================================================

import json
import csv
import os
import glob
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[ALCHEMIST]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DataAlchemist")

class PayloadCompiler:
    def __init__(self):
        self.input_dir = "outputs"
        self.output_dir = "datasets"
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def compile_datasets(self):
        logger.info("Initializing raw data schema scan...")
        
        json_files = glob.glob(f"{self.input_dir}/*.json")
        if not json_files:
            logger.warning("No payload vectors located inside outputs/. Execution halted.")
            return

        compiled_data = []
        all_keys = set()

        for file in json_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    
                    # Standardize structures into an iteration matrix
                    records = data if isinstance(data, list) else [data]
                    
                    for record in records:
                        if isinstance(record, dict):
                            compiled_data.append(record)
                            all_keys.update(record.keys())
            except Exception as e:
                logger.error(f"Failed to ingest vector file {file}: {e}")

        if not compiled_data:
            logger.warning("Zero valid dictionary matrices compiled. Aborting file write.")
            return

        # Explicitly sort headers for clean structural alignment
        headers = sorted(list(all_keys))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(self.output_dir, f"academic_dataset_{timestamp}.csv")

        try:
            with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
                # restval='' auto-fills missing keys with empty strings for FOSS normalization
                writer = csv.DictWriter(csvfile, fieldnames=headers, restval='')
                writer.writeheader()
                writer.writerows(compiled_data)
                
            logger.info(f"\033[1;32m[SUCCESS]\033[0m Transmuted {len(compiled_data)} heterogeneous records smoothly.")
            logger.info(f"Fields locked: {headers}")
            logger.info(f"Dataset securely exported to: {export_path}")
        except Exception as e:
            logger.error(f"Failed writing target dataset matrix: {e}")

if __name__ == "__main__":
    compiler = PayloadCompiler()
    compiler.compile_datasets()
