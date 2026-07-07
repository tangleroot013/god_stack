#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK | FULL PIPELINE EXECUTOR WITH PARSING HOOKS
# ==============================================================================
import logging
from god_scraper import GodScraper
from parsers.content_extractor import ContentExtractor

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;32m[PIPELINE-E2E]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PipelineE2E")

def run_unified_ingestion():
    logger.info("🎬 Initializing Complete Ingestion-to-Parsing Sequence...")
    
    target_url = "https://news.ycombinator.com/news"
    mock_body = "<html><body>Standard Source Tree containing real-time developer index feeds.</body></html>"
    
    # 1. Scrape & Route Layer
    scraper = GodScraper()
    pipeline_clear = scraper.process_target(target_url, mock_body)
    
    if pipeline_clear:
        # 2. Parse & Extract Layer (FOSS Extractor Component)
        structured_record = ContentExtractor.extract_payload(mock_body, target_url)
        logger.info("🎉 Structured record completed successfully:")
        print(f"\033[1;35mTitle:\033[0m {structured_record['title']}")
        print(f"\033[1;35mTimestamp:\033[0m {structured_record['extracted_at']}")
        print(f"\033[1;35mData Footprint:\033[0m {structured_record['content_length']} bytes")
    else:
        logger.error("❌ Node pipeline stopped before reaching extraction layer.")

if __name__ == "__main__":
    run_unified_ingestion()
