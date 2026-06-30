#!/usr/bin/env python3
import json
import time
import random
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# --- Thread-Safe Production Orchestrator ---
class DistributedHarvester:
    def __init__(self, output_csv="concurrent_research.csv"):
        self.output_csv = Path(output_csv)
        self.csv_lock = threading.Lock()
        self.fields = ["Timestamp", "Thread_ID", "Target_URL", "Execution_Time_ms", "Status"]
        self.initialize_ledger()

    def initialize_ledger(self):
        """Initializes headers on disk safely."""
        with self.csv_lock:
            with open(self.output_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writeheader()

    def process_node_worker(self, url):
        """Worker thread task execution loop."""
        thread_ident = threading.get_ident()
        start_time = time.time()
        
        # Simulate network extraction variability
        sleep_duration = random.uniform(0.3, 0.8)
        time.sleep(sleep_duration)
        
        # Introduce a controlled runtime anomaly
        status = "SUCCESS"
        if "timeout-node" in url:
            status = "TIMEOUT_QUARANTINED"
            
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        row_data = {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Thread_ID": f"Worker-{thread_ident}",
            "Target_URL": url,
            "Execution_Time_ms": elapsed_ms,
            "Status": status
        }
        
        # Thread-safe context flush to standard CSV ledger
        with self.csv_lock:
            with open(self.output_csv, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writerow(row_data)
                
        return row_data

    def execute_parallel_sweep(self, target_urls, max_workers=4):
        print(f"[*] Dispatching {len(target_urls)} tasks across {max_workers} thread vectors...")
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map futures to track background tasks
            future_to_url = {executor.submit(self.process_node_worker, url): url for url in target_urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    print(f"    [✔] Worker flushed data for: {url}")
                    results.append(data)
                except Exception as e:
                    print(f"    [💥] Worker thread crash intercepted on {url}: {e}")
                    
        return results

if __name__ == "__main__":
    test_targets = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://arxiv.org/list/cs.AI/recent",
        "https://www.nature.com/articles/d41586-026-00123-x",
        "https://timeout-node.invalid/api/v1/metrics", # Simulates error routing
        "https://en.wikipedia.org/wiki/Open-source_software",
        "https://github.com/trending"
    ]
    
    harvester = DistributedHarvester()
    
    print("====================================================")
    print("        RUNNING FEATURE 4 TEST SUITE                ")
    print("====================================================")
    
    start_total = time.time()
    harvested_matrix = harvester.execute_parallel_sweep(test_targets, max_workers=4)
    total_duration = time.time() - start_total
    
    print("\n[+] Parallel Verification Matrix Summary:")
    print(json.dumps(harvested_matrix, indent=2))
    print(f"\n[+] Performance Optimization: Handled 6 targets in {total_duration:.2f}s using pooled threads.")
