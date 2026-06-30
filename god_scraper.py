import asyncio
import random
from frontier_manager import Frontier
from network_backoff import NetworkBackoff
from dual_buffer import DualBuffer
from dead_letter_stream import DeadLetterStream
from metrics_exporter import NODES_PROCESSED, NODES_QUARANTINED, BUFFER_FILL

class GodScraper:
    def __init__(self):
        self.backoff = NetworkBackoff()
        self.buffer = DualBuffer(capacity=5)
        self.processed_count = 0

    async def flush_handler(self, data_chunk):
        print(f"\033[0;32m[FLUSH] Committing {len(data_chunk)} data records cleanly to storage ledger.\033[0m")
        # Attribute batch processing milestones to the central flusher execution unit
        NODES_PROCESSED.labels(worker_id="core_flusher").inc(len(data_chunk))
        await asyncio.sleep(0.01)

    async def fetch_node(self, url: str):
        if "node_105" in url:
            raise ConnectionResetError("403 Forbidden - Shield Triggered")
        if "malformed" in url:
            raise ValueError("Invalid structural layout syntax")
        return {"url": url, "status": "SUCCESS", "bytes": random.randint(250, 350)}

    async def worker_loop(self, worker_id: int):
        worker_label = f"worker_{worker_id}"
        while True:
            url = Frontier.get_next()
            if not url:
                break
            
            attempt = 0
            success = False
            while attempt < 3 and not success:
                try:
                    data = await self.fetch_node(url)
                    await self.buffer.append(data, self.flush_handler)
                    
                    # Track overall buffer fill state
                    BUFFER_FILL.set(len(self.buffer.primary_buffer) / self.buffer.capacity)
                    
                    success = True
                    self.processed_count += 1
                except (ConnectionResetError, ValueError) as err:
                    attempt += 1
                    if attempt >= 3:
                        DeadLetterStream.contain(url, str(err))
                        # Record structural errors with fine-grained context
                        NODES_QUARANTINED.labels(
                            worker_id=worker_label, 
                            error_type=type(err).__name__
                        ).inc()
                    else:
                        await self.backoff.wait(attempt)

    async def run(self):
        workers = [asyncio.create_task(self.worker_loop(i)) for i in range(4)]
        await asyncio.gather(*workers)
        
        # Safe rundown logic to sweep final buffer remnants
        if self.buffer.primary_buffer:
            BUFFER_FILL.set(len(self.buffer.primary_buffer) / self.buffer.capacity)
            await self.flush_handler(self.buffer.primary_buffer)
            BUFFER_FILL.set(0.0)
