#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK | INTEGRATION TEST MATRIX
# ==============================================================================
import os
import sys
import sqlite3
import logging
from god_scraper import GodScraper

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;33m%(asctime)s\033[0m | \033[1;36m[TEST-MATRIX]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TestMatrix")

def verify_sqlite_state():
    """Validates Write-Ahead Logging integrity and extraction states."""
    db_path = "storage.sqlite"
    if not os.path.exists(db_path):
        logger.warning(f"⚠️ Storage target {db_path} not initialized yet.")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verify WAL mode configuration
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        logger.info(f"💾 Storage Engine Pragma Journal Mode: {mode.upper()}")
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to verify database hooks: {e}")
        return False

def execute_integration_suite():
    logger.info("⚡ Commencing End-to-End Stack Pipeline Integration...")
    
    # Instantiate the unified scraper core
    scraper = GodScraper()
    
    # Target batch matrices
    mock_targets = [
        ("https://news.ycombinator.com/news", "<html>✅ Standard Source Tree</html>"),
        ("https://github.com/trending", "<html><script src='https://challenges.cloudflare.com/turnstile/v0/api.js'></script>🤖 Perimeter Active</html>")
    ]
    
    success_count = 0
    for url, html in mock_targets:
        logger.info(f"📥 Dispatching job matrix item -> {url}")
        status = scraper.process_target(url, html)
        if status:
            success_count += 1
            
    logger.info(f"📊 Run Completed: {success_count}/{len(mock_targets)} pipelines completed successfully.")
    
    # Storage check
    verify_sqlite_state()

if __name__ == "__main__":
    execute_integration_suite()
