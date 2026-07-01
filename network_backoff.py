import asyncio
import random
import logging

logger = logging.getLogger("god_stack.resilience")

class NetworkBackoff:
    def __init__(self, base_delay=0.1, max_delay=3.0, factor=2):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor

    async def wait(self, attempt: int):
        delay = min(self.max_delay, self.base_delay * (self.factor ** attempt))
        jittered_delay = random.uniform(0, delay)
        await asyncio.sleep(jittered_delay)
