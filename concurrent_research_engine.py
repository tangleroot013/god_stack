#!/usr/bin/env python3
import random
import time
import threading
from pathlib import Path
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed
from database_layer import SQLitePool, ResearchLedger

class ConcurrentResearchEngine:
    """Multi-worker research aggregator with thread-safe database persistence."""
    
    def __init__(self, target_file="bulk_targets.txt", num_workers=4):
        self.target_file = Path(target_file)
        self.num_workers = num_workers
        self.db_pool = SQLitePool()
        self.ledger = ResearchLedger(self.db_pool)
        
        # Per-worker metrics (thread-safe)
        self.metrics_lock = threading.Lock()
        self.worker_metrics = {
            f"worker_{i}": {"processed": 0, "success": 0, "quarantined": 0}
            for i in range(num_workers)
        }
        self.global_metrics = {"processed": 0, "success": 0, "quarantined": 0}
        self.start_time = None
    
    def bootstrap_targets(self):
        """Ensures target list exists."""
        if not self.target_file.exists():
            sample_targets = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://arxiv.org/list/cs.AI/recent",
                "https://www.nature.com/articles/d41586-026-00123-x",
                "https://www.nature.com/articles/nature-genomics",
                "https://cluster.example.com/api/v1/node_105",
                "https://github.com/openai/gpt-4-research",
                "https://www.science.org/doi/10.1126/science.abn2100",
                "https://pubmed.ncbi.nlm.nih.gov/research-trends"
            ]
            self.target_file.write_text("\n".join(sample_targets))
            print(f"[+] Initialized target profile layout at: {self.target_file}")
    
    def process_url(self, url, worker_id):
        """Process a single URL (called by worker thread)."""
        domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"
        
        # Simulate adaptive network jitter
        time.sleep(random.uniform(0.3, 0.8))
        
        # Defensive quarantine logic
        if "node_105" in url or "malformed" in url:
            status = "QUARANTINED"
            error_type = "403_Forbidden"
            title = "N/A"
            summary = "BLOCKED: Defensive trigger or network rejection."
            success = False
        else:
            status = "SUCCESS"
            error_type = None
            title = f"Deep Dive Analysis: {domain.capitalize()}"
            summary = "Cleaned structural layout contents successfully extracted."
            success = True
        
        row_data = {
            "Source_Domain": domain,
            "Target_URL": url,
            "Research_Title": title,
            "Extracted_Text_Summary": summary,
            "Status": status,
            "Error_Type": error_type,
            "Worker_ID": worker_id
        }
        
        # Thread-safe database insert
        self.ledger.insert_record(row_data)
        
        # Update thread-local metrics
        with self.metrics_lock:
            self.worker_metrics[worker_id]["processed"] += 1
            if success:
                self.worker_metrics[worker_id]["success"] += 1
            else:
                self.worker_metrics[worker_id]["quarantined"] += 1
            self.global_metrics["processed"] += 1
            self.global_metrics["success"] += (1 if success else 0)
            self.global_metrics["quarantined"] += (0 if success else 1)
        
        # Live feedback
        status_symbol = "✅" if success else "⚠️"
        print(f"[{worker_id}] {status_symbol} {url}")
        
        return row_data
    
    def execute_concurrent_run(self):
        """Execute research pipeline with thread pool."""
        self.bootstrap_targets()
        urls = [line.strip() for line in self.target_file.read_text().splitlines() if line.strip()]
        
        print("\n" + "="*60)
        print(" CONCURRENT RESEARCH AGGREGATOR ")
        print(f" Workers: {self.num_workers} | Targets: {len(urls)}")
        print("="*60 + "\n")
        
        self.start_time = time.time()
        
        # Distribute work across thread pool
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = {
                executor.submit(self.process_url, url, f"worker_{i % self.num_workers}"): url
                for i, url in enumerate(urls)
            }
            
            # Wait for all futures to complete
            completed = 0
            for future in as_completed(futures):
                completed += 1
                url = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"[ERROR] Failed to process {url}: {e}")
        
        # Final metrics from database
        elapsed_time = time.time() - self.start_time
        db_metrics = self.ledger.get_metrics()
        
        print("\n" + "="*60)
        print(" RUN COMPLETE ")
        print("="*60)
        print(f"Elapsed Time: {elapsed_time:.2f}s")
        print(f"Throughput: {len(urls) / elapsed_time:.2f} URLs/sec")
        print(f"Total Processed: {db_metrics['total']}")
        print(f"Successful: {db_metrics['success']}")
        print(f"Quarantined: {db_metrics['quarantined']}")
        print("\nPer-Worker Breakdown:")
        for worker_id, metrics in self.worker_metrics.items():
            print(f"  {worker_id}: {metrics['processed']} processed, {metrics['success']} success, {metrics['quarantined']} quarantined")
        print("="*60 + "\n")

if __name__ == "__main__":
    engine = ConcurrentResearchEngine(num_workers=4)
    engine.execute_concurrent_run()
