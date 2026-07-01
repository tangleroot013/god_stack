import asyncio
import logging

logger = logging.getLogger("god_stack.buffer")

class DualBuffer:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.primary_buffer = []
        self.secondary_buffer = []
        self.flush_lock = asyncio.Lock()

    async def append(self, item, flush_callback):
        self.primary_buffer.append(item)
        if len(self.primary_buffer) >= self.capacity:
            async with self.flush_lock:
                if len(self.primary_buffer) >= self.capacity:
                    self.secondary_buffer = self.primary_buffer
                    self.primary_buffer = []
                    asyncio.create_task(self._safe_flush(flush_callback))

    async def _safe_flush(self, flush_callback):
        try:
            if self.secondary_buffer:
                await flush_callback(self.secondary_buffer)
                self.secondary_buffer.clear()
        except Exception as e:
            print(f"[BUFFER ERROR] Flush failure: {e}")
