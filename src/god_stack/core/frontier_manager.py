import threading
from collections import deque

class FrontierManager:
    def __init__(self):
        self._queue = deque()
        self._lock = threading.Lock()
        self.visited = set()

    def add_url(self, url: str):
        with self._lock:
            if url not in self.visited:
                self.visited.add(url)
                self._queue.append(url)
                return True
        return False

    def get_next(self):
        with self._lock:
            if self._queue:
                return self._queue.popleft()
        return None

    def size(self):
        with self._lock:
            return len(self._queue)

Frontier = FrontierManager()
