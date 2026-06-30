#!/usr/bin/env python3
import asyncio
import os
import csv
from datetime import datetime
import time

# Core Framework Modules
from god_engine import GodEngineNode
from engine_extension_core import DynamicRateLimiter, DataSanitizer, PayloadLedger
from telemetry_monitor import TelemetryMonitor
from matrix_pool_loader import MatrixPoolLoader

async def run_headless_system():
    print("\033[0;35m[INIT] Starting Headless G.O.D. Stack Extraction Loop...\033[0m")
    
    # Initialize Engine Infrastructure Modules
    loader = MatrixPoolLoader()
    limiter = DynamicRateLimiter()
    sanitizer = DataSanitizer()
    ledger = PayloadLedger()
    telemetry = TelemetryMonitor()

    # Define paths
    manifest_file = "bulk_targets.txt"
    export_filepath = os.path.join("outputs", "headless_extraction_matrix.csv")
    
    # Generate a quick input manifest file if one doesn't exist yet
    if not os.path.exists(manifest_file):
        with open(manifest_file, "w") as f:
            f.write("https://example.com/stream_node_v2_0\n")
            f.write("https://example.com/stream_node_v2_1\n")
            f.write("https://example.com/stream_node_v2_0\n") # Intentional duplicate entry

    try:
        # Load targets through the generator filtering layer
        targets = list(loader.yield_targets_from_file(manifest_file))
    except Exception as err:
        print(f"Manifest loading aborted: {err}")
        return

    final_dataset = []

    try:
        await GodEngineNode.initialize(headless=True)
        
        for index, url in enumerate(targets, start=1):
            # Check duplicate tracking engine cache signatures
            if ledger.is_duplicate(url):
                print(f" -> [LEDGER BYPASS] Skipped repeating target: {url}")
                telemetry.record_run(0, 0, was_duplicate=True)
                continue

            # Apply pacing delay
            print(f" -> [THROTTLE] Holding pattern for {limiter.current_delay:.2f}s...")
            await limiter.throttle()

            print(f"\033[0;36mProcessing Ingestion Node [{index}/{len(targets)}]: {url}\033[0m")
            
            start_clock = time.perf_counter()
            frame = await GodEngineNode.fetch_and_extract(url)
            elapsed_ms = int((time.perf_counter() - start_clock) * 1000)

            # Adapt the pacing engine to match network response times
            limiter.adjust_velocity(elapsed_ms)

            if frame["status"] == "SUCCESS":
                clean_title = sanitizer.clean_string(frame["extracted_data"]["title"])
                bytes_in = frame["metrics"]["payload_bytes"]
                
                final_dataset.append({
                    "URL": url,
                    "Status": "SUCCESS",
                    "Title": clean_title,
                    "Bytes Recieved": bytes_in,
                    "Links Discovered": frame["metrics"]["discovered_anchors_count"],
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                telemetry.record_run(execution_ms=elapsed_ms, payload_bytes=bytes_in)
            else:
                final_dataset.append({
                    "URL": url,
                    "Status": "FAILED",
                    "Title": "N/A",
                    "Bytes Recieved": 0,
                    "Links Discovered": 0,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                telemetry.record_run(execution_ms=elapsed_ms, payload_bytes=0, was_fault=True)

        await GodEngineNode.shutdown()

        # Write results down to spreadsheet storage
        if final_dataset:
            fields = ["URL", "Status", "Title", "Bytes Recieved", "Links Discovered", "Timestamp"]
            with open(export_filepath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(final_dataset)
            print(f"\033[0;32m[EXPORT] Data matrix written down to workspace target: {export_filepath}\033[0m")

        # Compile and generate telemetry session logs
        report_path = telemetry.compile_session_report()
        print(f"\033[0;32m[TELEMETRY] Run performance stats logged at: {report_path}\033[0m")

    except Exception as loop_fault:
        print(f"\033[0;31mSystem runtime processing exception caught: {loop_fault}\033[0m")

if __name__ == "__main__":
    asyncio.run(run_headless_system())
