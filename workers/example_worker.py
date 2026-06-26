import asyncio
from utils.logger import setup_production_logging

log = setup_production_logging()

async def run_example_payload():
    log.info("⚙️ Example worker initialized. Executing payload...")
    try:
        await asyncio.sleep(2)
        log.info("✅ Example worker payload execution completed successfully.")
    except Exception as e:
        log.error(f"❌ Example worker encountered a critical failure: {e}", exc_info=True)
        raise
