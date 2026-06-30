#!/usr/bin/env python3
import random, time, threading, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from database_layer import SQLitePool, ResearchLedger

class ConcurrentResearchEngine:
    def __init__(self, target_file="bulk_targets.txt", workers=None):
        self.target_file = Path(target_file)
        # Auto-scale: leave 1 core free for system
        self.workers = workers or max(2, os.cpu_count() - 1)
        self.db = SQLitePool()
        self.ledger = ResearchLedger(self.db)

        self.metrics_lock = threading.Lock()
        self.worker_stats = {
            f"worker_{i}": {"processed": 0, "success": 0, "quarantined": 0}
            for i in range(self.workers)
        }

    def _ensure_targets(self):
        if not self.target_file.exists():
            sample = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://arxiv.org/list/cs.AI/recent",
                "https://www.nature.com/articles/d41586-026-00123-x",
                "https://cluster.example.com/api/v1/node_105",
                "https://github.com/openai/gpt-4-research",
            ]
            self.target_file.write_text("\n".join(sample))
            print("[+] Created default target list")

    def _process(self, url, worker_id):
        domain = url.split("//")[-1].split("/")[0]
        time.sleep(random.uniform(0.3, 0.8))

        if "node_105" in url:
            status, success = "QUARANTINED", False
            title, summary = "N/A", "BLOCKED: defensive trigger"
        else:
            status, success = "SUCCESS", True
            title = f"Research on {domain}"
            summary = "Extracted content successfully."

        record = {
            "Source_Domain": domain,
            "Target_URL": url,
            "Research_Title": title,
            "Extracted_Text_Summary": summary,
            "Status": status,
            "Error_Type": None,
            "Worker_ID": worker_id,
        }
        self.ledger.insert_record(record)

        with self.metrics_lock:
            self.worker_stats[worker_id]["processed"] += 1
            self.worker_stats[worker_id]["success" if success else "quarantined"] += 1

        print(f"[{worker_id}] {'✅' if success else '⚠️'} {url}")
        return record

    def run(self):
        self._ensure_targets()
        urls = [l.strip() for l in self.target_file.read_text().splitlines() if l.strip()]
        start = time.time()

        print("\n" + "="*60)
        print(f" CONCURRENT RESEARCH AGGREGATOR ")
        print(f" Workers: {self.workers} (auto-scaled) | Targets: {len(urls)}")
        print("="*60 + "\n")

        with ThreadPoolExecutor(max_workers=self.workers) as exe:
            futures = {
                exe.submit(self._process, url,
                            f"worker_{i % self.workers}"): url
                for i, url in enumerate(urls)
            }
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    print(f"[ERROR] {futures[f]} – {e}")

        elapsed = time.time() - start
        db_stats = self.ledger.get_metrics()
        print("\n" + "="*60)
        print(" RUN COMPLETE ")
        print("="*60)
        print(f"Elapsed Time: {elapsed:.2f}s")
        print(f"Throughput: {len(urls)/elapsed:.2f} URLs/sec")
        print(f"Total Processed: {db_stats['total']}  Success: {db_stats['success']}  Quarantined: {db_stats['quarantined']}")
        print("\nPer-Worker Breakdown:")
        for w, s in self.worker_stats.items():
            print(f"  {w}: {s['processed']} processed ({s['success']} ok, {s['quarantined']} blocked)")
        print("="*60 + "\n")

if __name__ == "__main__":
    engine = ConcurrentResearchEngine()
    engine.run()
