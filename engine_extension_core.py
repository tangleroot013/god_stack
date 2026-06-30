#!/usr/bin/env python3
import re
import asyncio

class DynamicRateLimiter:
    def __init__(self, base_delay=0.3, max_delay=4.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.current_delay = base_delay

    async def throttle(self):
        await asyncio.sleep(self.current_delay)

    def adjust_velocity(self, response_time_ms):
        if response_time_ms > 1000:
            self.current_delay = min(self.max_delay, self.current_delay * 1.4)
        elif response_time_ms < 400:
            self.current_delay = max(self.base_delay, self.current_delay * 0.85)

class DataSanitizer:
    @staticmethod
    def clean_string(raw_text):
        if not raw_text:
            return "N/A"
        clean = re.sub(r'\s+', ' ', raw_text).strip()
        clean = re.sub(r'[^\x20-\x7E]', '', clean)
        return clean[:120]

class PayloadLedger:
    def __init__(self):
        self.visited_matrix = set()

    def is_duplicate(self, url):
        if url in self.visited_matrix:
            return True
        self.visited_matrix.add(url)
        return False

    def purge_ledger(self):
        self.visited_matrix.clear()
