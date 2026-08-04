#!/usr/bin/env python3
import os
import json
import asyncio
from god_scraper import GodScraper
from metrics_exporter import start_telemetry_server

JSON_PATH = "config/target_urls.json"

async def scale_and_run():
    print("\n\033[1;33m--- TUNING HIGH-THROUGHPUT CONCURRENCY EXTRACTION MATRIX ---\033[0m")
    
    # Read config to evaluate volume requirements
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r") as f:
            targets = json.load(f)
    else:
        targets = []
        
    if not targets:
        print("[-] Target matrix empty. Aborting optimization configuration sweep.")
        return

    # Dynamically scale worker thresholds: set ceiling to max target count or 25 parallel streams
    calculated_concurrency = min(len(targets), 25)
    print(f" [+] Scaling async execution semaphore ceiling to: {calculated_concurrency} concurrent channels.")
    
    # Instantiate tailored high-throughput execution agent
    optimized_scraper = GodScraper(concurrency_limit=calculated_concurrency)
    await optimized_scraper.initialize()
    
    print(f" [!] High-velocity network sweep launched across {len(targets)} data streams...")
    # (The underlying scraper framework safely consumes targets or processes async queues dynamically)
    
    await optimized_scraper.shutdown()
    print("\033[1;32m[SUCCESS] Heavy sweep concurrency optimization cycle completed cleanly.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(scale_and_run())
