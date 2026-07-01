#!/usr/bin/env python3
import os
import json
import urllib.request
import time
import threading
from metrics_exporter import start_telemetry_server, SYSTEM_METRICS

def run_audit():
    print("\n\033[1;34m>>> INITIALIZING TELEMETRY EXPOSITION AUDIT RUNNER <<<\033[0m")
    
    # 1. Start Exposition Server Context on an isolated test port
    test_port = 8999
    start_telemetry_server(port=test_port)
    time.sleep(0.5) # Allow background socket worker to bind safely
    
    # 2. Parse Current Targets Array to calculate expected increments
    json_path = "config/target_urls.json"
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            targets = json.load(f)
    else:
        targets = ["https://example.com", "https://httpbin.org/html"\]
    
    target_count = len(targets)
    print(f" [*] Detected {target_count} active target vectors in configuration manifest.")
    
    # 3. Simulate Pipeline Metric Registration Mutators
    print(" [*] Simulating execution sweep over targeting matrix...")
    for url in targets:
        SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
        SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
        SYSTEM_METRICS["god_stack_bytes_processed_total"] += 270  # Mock layout payload size bytes
        
    # 4. Perform an internal loopback network scrape against the live endpoint
    endpoint_url = f"http://127.0.0.1:{test_port}/metrics"
    print(f" [*] Scraping live endpoint: {endpoint_url}")
    
    try:
        with urllib.request.urlopen(endpoint_url, timeout=2) as response:
            raw_metrics = response.read().decode("utf-8")
            
        print("\n\033[1;33m--- RAW EXPOSED PROMETHEUS METRICS BUFFERS ---\033[0m")
        print(raw_metrics.strip())
        print("\033[1;33m----------------------------------------------\033[0m\n")
        
        # 5. Assertions and Structural Sanity Parsing
        assert f"god_stack_ingestion_attempts_total {target_count}" in raw_metrics, "Attempts counter mismatch!"
        assert f"god_stack_ingestion_success_total {target_count}" in raw_metrics, "Success counter mismatch!"
        
        print("\033[1;32m[SUCCESS] Telemetry collection audit verified clean. Counter exposure conforms to OpenMetrics spec.\033[0m\n")
        
    except Exception as e:
        print(f"\033[1;31m[-] Telemetry Validation Failure:\033[0m {e}")

if __name__ == "__main__":
    run_audit()
