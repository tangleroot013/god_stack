import asyncio
import uuid
import logging
from utils.work_queue import DistributedWorkQueue
from god_scraper import GodScraper

worker_id = f"worker-{uuid.uuid4().hex[:6]}"
logging.basicConfig(level=logging.INFO, format=f"\033[1;34m%(asctime)s\033[0m | \033[1;32m[{worker_id.upper()}]\033[0m %(message)s")
logger = logging.getLogger("WorkerNode")

async def run_worker():
    queue = DistributedWorkQueue()
    scraper = GodScraper()
    await scraper.initialize(headless=True)
    logger.info("Node linked to core task ledger broker. Polling for workflows...")
    
    try:
        while True:
            task = queue.lease_task(worker_id)
            if not task:
                logger.info("Ledger cold. Standing down for 5s...")
                await asyncio.sleep(5)
                continue
            
            task_id, target_url = task
            logger.info(f"Lease secured on task segment [{task_id}]: {target_url}")
            
            result = await scraper.scrape(target_url, [{"action": "scroll"}])
            if result.get("status") == "success":
                logger.info(f"Node successfully synchronized target [{task_id}]")
                queue.complete_task(task_id)
            else:
                logger.error(f"Execution fault at node [{task_id}]: {result.get('message')}")
                queue.fail_task(task_id)
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        await scraper.shutdown()

if __name__ == "__main__":
    asyncio.run(run_worker())
