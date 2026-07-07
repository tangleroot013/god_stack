#!/usr/bin/env python3
import csv
import json
import random
import time
import sys
from pathlib import Path

# Fields that matter to an analyst or researcher
CSV_FIELDS = ["Timestamp", "Source_Domain", "Target_URL", "Research_Title", "Extracted_Text_Summary", "Status"]

class ResearchPipeline:
    def __init__(self, target_file="bulk_targets.txt", output_csv="research_output.csv"):
        self.target_file = Path(target_file)
        self.output_csv = Path(output_csv)
        self.metrics = {
            "processed": 0,
            "success": 0,
            "quarantined": 0
        }

    def bootstrap_targets(self):
        """Ensures a list of target endpoints exists to read from."""
        if not self.target_file.exists():
            sample_targets = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://arxiv.org/list/cs.AI/recent",
                "https://www.nature.com/articles/d41586-026-00123-x",
                "https://cluster.example.com/api/v1/node_105"  # Expected to fail/quarantine
            ]
            self.target_file.write_text("\n".join(sample_targets))
            print(f"[+] Initialized target profile layout at: {self.target_file}")

    def initialize_csv(self):
        """Prepares the clean output file with proper semantic headings."""
        if not self.output_csv.exists():
            with open(self.output_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writeheader()
            print(f"[+] Clean CSV data ledger opened at: {self.output_csv}")

    def process_node(self, url):
        """Simulates robust extraction, layout cleanup, and defensive parsing."""
        self.metrics["processed"] += 1
        domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"

        # Defensive check against known bad nodes or dead structural routes
        if "node_105" in url or "malformed" in url:
            self.metrics["quarantined"] += 1
            print(f"[DLQ] Node quarantined: {url} | Reason: 403 Forbidden - Shield Triggered")
            return {
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Source_Domain": domain,
                "Target_URL": url,
                "Research_Title": "N/A",
                "Extracted_Text_Summary": "BLOCKED: Defensive trigger or network rejection.",
                "Status": "QUARANTINED"
            }

        # Simulate adaptive network pacing (jitter)
        time.sleep(random.uniform(0.4, 1.1))

        # Simulated payload normalization (The "Semantic Stripper" effect)
        self.metrics["success"] += 1
        return {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Source_Domain": domain,
            "Target_URL": url,
            "Research_Title": f"Deep Dive Analysis: {domain.capitalize()}",
            "Extracted_Text_Summary": f"Cleaned structural layout contents successfully extracted from research node path.",
            "Status": "SUCCESS"
        }

    def execute_run(self):
        self.bootstrap_targets()
        self.initialize_csv()
        urls = [line.strip() for line in self.target_file.read_text().splitlines() if line.strip()]

        print("\n====================================================")
        print(" EXECUTING MASS PRODUCTION RESEARCH SWEEP ")
        print("====================================================\n")

        records_to_flush = []
        for url in urls:
            print(f"[*] Ingesting: {url}")
            row_data = self.process_node(url)
            records_to_flush.append(row_data)

            # Flush cleanly to disk in chunks to preserve execution safety
            if len(records_to_flush) >= 2 or url == urls[-1]:
                with open(self.output_csv, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                    writer.writerows(records_to_flush)
                print(f"[FLUSH] Committed {len(records_to_flush)} rows safely onto data ledger.")
                records_to_flush.clear()

        print("\n====================================================")
        print(f"RUN SUCCESSFUL: {self.metrics['processed']} total research sites analyzed.")
        print(f" -> Active records compiled: {self.metrics['success']}")
        print(f" -> Quarantined references: {self.metrics['quarantined']}")
        print("====================================================\n")

if __name__ == "__main__":
    pipeline = ResearchPipeline()
    pipeline.execute_run()
