#!/usr/bin/env python3
import time
import json
import os
from datetime import datetime

class TelemetryMonitor:
    def __init__(self, log_dir="outputs"):
        self.log_dir = log_dir
        self.start_time = time.time()
        self.metrics_registry = {
            "session_start": datetime.now().isoformat(),
            "total_processed": 0,
            "total_duplicates_bypassed": 0,
            "total_payload_bytes": 0,
            "latency_history_ms": [],
            "execution_faults": 0
        }
        os.makedirs(log_dir, exist_ok=True)

    def record_run(self, execution_ms, payload_bytes, was_duplicate=False, was_fault=False):
        """Ingests live transaction statistics from the scraper execution loop."""
        if was_duplicate:
            self.metrics_registry["total_duplicates_bypassed"] += 1
            return
        if was_fault:
            self.metrics_registry["execution_faults"] += 1
            return
            
        self.metrics_registry["total_processed"] += 1
        self.metrics_registry["total_payload_bytes"] += payload_bytes
        self.metrics_registry["latency_history_ms"].append(execution_ms)

    def compile_session_report(self):
        """Calculates historical throughput efficiency metrics and compiles a JSON snapshot."""
        latencies = self.metrics_registry["latency_history_ms"]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        elapsed_time = time.time() - self.start_time
        
        report = {
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "runtime_seconds": round(elapsed_time, 2)
            },
            "throughput": {
                "nodes_ingested_successfully": self.metrics_registry["total_processed"],
                "duplicate_skips": self.metrics_registry["total_duplicates_bypassed"],
                "network_faults_registered": self.metrics_registry["execution_faults"],
                "volume_mb": round(self.metrics_registry["total_payload_bytes"] / (1024 * 1024), 4)
            },
            "performance_latency": {
                "average_node_response_ms": round(avg_latency, 2),
                "peak_burst_latency_ms": max(latencies) if latencies else 0
            }
        }
        
        output_path = os.path.join(self.log_dir, "session_telemetry_snapshot.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)
        
        return output_path

if __name__ == "__main__":
    # Test execution confirmation pass
    monitor = TelemetryMonitor()
    monitor.record_run(execution_ms=240, payload_bytes=10245)
    monitor.record_run(execution_ms=1150, payload_bytes=14201)
    monitor.record_run(execution_ms=0, payload_bytes=0, was_duplicate=True)
    saved_at = monitor.compile_session_report()
    print(f"\033[0;32m[TELEMETRY CONFIG] Test pass compiled. Snapshot validated at: {saved_at}\033[0m")
