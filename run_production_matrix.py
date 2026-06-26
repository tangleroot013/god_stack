#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK | FULL INGESTION -> PARSING -> STORAGE -> TELEMETRY MATRICES
# ==============================================================================
import time
import logging
from god_scraper import GodScraper
from parsers.content_extractor import ContentExtractor
from data_storage_sync import StorageSyncEngine
import metrics_exporter

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[MATRIX-E2E]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MatrixE2E")

def execute_matrix_pipeline():
    logger.info("⚡ Activating Complete Ingestion to Storage Matrix Loop...")
    
    # Start the metric exposition server thread
    metrics_exporter.start_telemetry_server(8000)
    
    scraper = GodScraper()
    storage = StorageSyncEngine()
    
    target_stream = [
        ("https://github.com/trending", "<html>Trending repositories context layer</html>"),
        ("https://github.com/trending", "<html>Trending repositories context layer</html>"), # Duplicate
        ("https://news.ycombinator.com/news", "<html>Standard Hacker News Document</html>")
    ]
    
    for idx, (url, html) in enumerate(target_stream, start=1):
        logger.info(f"▶️ Processing Pipeline Task Frame #{idx} -> {url}")
        metrics_exporter.SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
        
        if scraper.process_target(url, html):
            metrics_exporter.SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
            structured_record = ContentExtractor.extract_payload(html, url)
            
            # Sync to SQLite WAL, checking for deduplication
            is_new = storage.sync_record(structured_record)
            if is_new:
                metrics_exporter.SYSTEM_METRICS["god_stack_bytes_processed_total"] += structured_record["content_length"]
            else:
                metrics_exporter.SYSTEM_METRICS["god_stack_deduplication_skips_total"] += 1
                
        print("-" * 72)
        time.sleep(0.5)

    # Output an administrative curl verification check
    logger.info("📡 Simulating local target scrape verification check from Prometheus port...")
    import urllib.request
    try:
        metrics_payload = urllib.request.urlopen("http://localhost:8000/metrics").read().decode("utf-8")
        print("\n\033[1;36m=== EXPOSED PROMETHEUS SCRAPE PAYLOAD ===\033[0m")
        print(metrics_payload)
    except Exception as e:
        logger.error(f"Failed to query metrics endpoint: {e}")

if __name__ == "__main__":
    import time
    while True:
        try:
            execute_matrix_pipeline()
        except Exception as e:
            print(f"[GOD-ENGINE] ❌ Pipeline runtime exception: {e}")
        print("[GOD-ENGINE] ⏳ Cycle complete. Retention hold active: Keeping port 8000 open for Prometheus...")
        time.sleep(15)
    import time
    print('[GOD-ENGINE] ⏳ Holding socket open for 15s for Prometheus scrape...')
    time.sleep(15)
