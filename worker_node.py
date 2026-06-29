import asyncio
import json
import os
import sys
import uuid
import socket
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List

from core.extension_loader import ExtensionLoader
from god_engine import GodEngineNode
from metrics_exporter import SYSTEM_METRICS

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;36m[WORKER-NODE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("WorkerNode")

class GodWorkerNode:
    def __init__(self, master_url: str, concurrency_limit: int = 3):
        self.master_url = master_url
        self.worker_id = f"node-{socket.gethostname()}-{uuid.uuid4().hex[:6]}"
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.extension_mgr = ExtensionLoader(plugin_dir="parsers")
        self.active = False

    async def initialize(self):
        """Asynchronously triggers underlying browser layers and hot-mounts plugins."""
        logger.info(f"Bootstrapping decentralized matrix environment frame: \033[1;32m{self.worker_id}\033[0m")
        await GodEngineNode.initialize(headless=True)
        await self.extension_mgr.discover_and_mount()
        self.active = True

    def _sync_post(self, url: str, payload: dict) -> tuple:
        """Symmetric underlying network dispatcher utilizing native urllib channels."""
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            url, data=data, 
            headers={'Content-Type': 'application/json'}, 
            method='POST'
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status, response.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            return e.code, ""
        except Exception:
            return 500, ""

    async def fetch_lease_batch(self, batch_size: int = 2) -> List[str]:
        """Polls the coordinator data boundary to lease available routing slots."""
        endpoint = f"{self.master_url}/api/frontier/lease"
        payload = {"worker_id": self.worker_id, "batch_size": batch_size}
        
        status, response_body = await asyncio.to_thread(self._sync_post, endpoint, payload)
        
        if status == 200 and response_body:
            try:
                return json.loads(response_body).get("targets", [])
            except Exception:
                return []
        return []

    async def ship_processed_payload(self, payload: Dict[str, Any]):
        """Streams transformed payload structures directly back to the data lake synchronization hub."""
        endpoint = f"{self.master_url}/api/storage/sync"
        packet = {"worker_id": self.worker_id, "data": payload}
        
        status, _ = await asyncio.to_thread(self._sync_post, endpoint, packet)
        if status == 200:
            SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
        else:
            logger.error(f"Master storage node rejected state payload submission window. Code: {status}")

    async def execute_task_vector(self, url: str):
        """Processes an assigned target URL under localized concurrency throttling limits."""
        async with self.semaphore:
            if not self.active:
                return
            
            SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1
            logger.info(f"Acquired system execution locks. Driving target vectors: {url}")
            
            try:
                # 1. Execute unblocking document parsing through standard underlying loops
                raw_result = await GodEngineNode.fetch_and_extract(url)
                
                # Check status flags emitted directly out of the core rendering matrix
                if raw_result.get("status") == "SUCCESS" or "SUCC" in raw_result.get("status", ""):
                    # 2. Run payload transformations across active dynamic plug-and-drop frameworks
                    enriched_result = await self.extension_mgr.pipeline_broadcast(raw_result)
                    
                    # 3. Transmit state blocks back over the cluster synchronization layer
                    await self.ship_processed_payload(enriched_result)
                else:
                    logger.warning(f"Aborting downstream synchronization pipeline execution for failed target: {url}")
            except Exception as e:
                logger.error(f"Critical task thread-pool runtime failure inside vector processing execution loops: {str(e)}")

    async def run_worker_loop(self):
        """Long-lived ingestion loop monitoring coordination boundaries."""
        await self.initialize()
        logger.info("Decentralized worker system active. Polling coordinator state matrix...")
        
        while self.active:
            targets = await self.fetch_lease_batch(batch_size=2)
            
            if not targets:
                logger.info("Frontier queue paths returned drained or empty. Cooling down loop pipelines...")
                break
                
            logger.info(f"Lease matrix successfully claimed for [{len(targets)}] target urls. Forking async worker channels...")
            tasks = [asyncio.create_task(self.execute_task_vector(url)) for url in targets]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.2)

    async def shutdown(self):
        """Clean teardown hook executing atomic resource de-allocations."""
        logger.warning("Intercepted shutdown notification sequence. Disconnecting grid layers...")
        self.active = False
        await self.extension_mgr.terminate_extensions()
        await GodEngineNode.shutdown()
        logger.info("Worker instance context cleanly unmounted.")
