#!/usr/bin/env python3
# ==============================================================================
# test_production_matrix.py – Pipeline Integrity Verification Script
# ==============================================================================
import asyncio
import os
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;32m[TEST-VERIFY]\033[0m %(message)s"
)
logger = logging.getLogger("TestMatrix")

async def run_pipeline_test():
    logger.info("⚡ Initiating Production Matrix compilation & runtime validation...")
    
    # 1. Test Compilation / Importability
    try:
        from run_production_matrix import ProductionMatrix
        logger.info("✅ Import validation: ProductionMatrix successfully compiled.")
    except Exception as e:
        logger.error(f"❌ Import validation failed: {e}")
        sys.exit(1)
        
    # 2. Instantiate and Check State Integrity
    try:
        matrix = ProductionMatrix()
        test_url = "https://news.ycombinator.com/best"
        matrix.add_job(test_url)
        
        if test_url not in matrix.jobs:
            raise ValueError("Job registration matrix mismatch; URL queue missing target.")
        logger.info("✅ Queue validation: Jobs are successfully registering in scope.")
    except Exception as e:
        logger.error(f"❌ State validation failed: {e}")
        sys.exit(1)

    # 3. Simulate Execution Pipeline Run
    try:
        logger.info("🔄 Launching isolated async execution pump...")
        await matrix.process_pipeline(test_url, idx=1)
        matrix.exporter.close()
        logger.info("✅ Execution validation: Pipeline processed to completion without blocks.")
    except Exception as e:
        logger.error(f"❌ Pipeline runtime execution failed: {e}")
        sys.exit(1)

    # 4. Final System Health Check
    logger.info("\n==================================================")
    logger.info("🎉 SUCCESS: All target matrix scripts are verified!")
    logger.info("==================================================")

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())
