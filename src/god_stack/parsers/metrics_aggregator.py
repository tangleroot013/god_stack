#!/usr/bin/env python3
# ==============================================================================
# STRUCTURED DATA PARSER & METRICS AGGREGATOR (metrics_aggregator.py)
# Architecture: High-Performance Output Analysis & Data Transformation Layer
# ==============================================================================

import os
import sys
import json
import logging
from glob import glob
from datetime import datetime

# Enforce clean workspace boundaries
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[METRICS-PARSER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MetricsParser")

class MetricsAggregator:
    def __init__(self, workspace_root: str):
        self.outputs_dir = os.path.join(workspace_root, "outputs")
        self.summary_file = os.path.join(self.outputs_dir, "dashboard_summary.json")

    def process_payload_batch(self) -> dict:
        logger.info(f"Scanning target matrix volume path: {self.outputs_dir}")
        target_files = glob(os.path.join(self.outputs_dir, "intel_*.json"))
        
        if not target_files:
            logger.warning("Data collection frame is empty. Zero source payloads located.")
            return {}

        total_bytes_processed = 0
        domain_frequency = {}
        processed_records = []

        logger.info(f"Discovered {len(target_files)} unparsed ingestion frames. Initializing map-reduce sequence...")

        for file_path in target_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Extract specific structural keys from standard matrix format
                target_url = data.get("target_url", "unknown")
                domain_ctx = data.get("domain_context", {})
                domain_name = domain_ctx.get("domain", "unknown_domain")
                content_len = data.get("content_length", 0)

                total_bytes_processed += content_len
                domain_frequency[domain_name] = domain_frequency.get(domain_name, 0) + 1
                
                processed_records.append({
                    "file": os.path.basename(file_path),
                    "url": target_url,
                    "size_bytes": content_len,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as read_fault:
                logger.error(f"Failed to decode segment file {file_path}: {str(read_fault)}")

        # Build compiled telemetry footprint
        summary_manifest = {
            "telemetry_meta": {
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_files_parsed": len(target_files),
                "aggregated_volume_kb": round(total_bytes_processed / 1024, 2)
            },
            "domain_distribution": domain_frequency,
            "manifest_registry": processed_records
        }

        # Write out to unified storage schema
        try:
            with open(self.summary_file, "w", encoding="utf-8") as out:
                json.dump(summary_manifest, out, indent=2)
            logger.info(f"\033[1;32m[SUCCESS]\033[0m Refined analysis matrix generated -> {self.summary_file}")
        except Exception as write_fault:
            logger.error(f"Failed to commit global metrics map: {str(write_fault)}")

        return summary_manifest

if __name__ == "__main__":
    WORKSPACE = os.path.expanduser("~/god_stack")
    aggregator = MetricsAggregator(WORKSPACE)
    aggregator.process_payload_batch()
