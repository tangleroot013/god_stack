import logging
from collections import deque
from urllib.parse import urlparse
from courlan_router import CourlanRouter

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;34m[FRONTIER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("FrontierManager")

class FrontierManager:
    def __init__(self):
        self.seen_urls = set()
        self.domain_buckets = {}
        self.domain_order = deque()
        self._metrics = {
            "frontier.enqueue": 0,
            "frontier.dequeue": 0,
            "frontier.trap_dropped": 0
        }

    def enqueue_batch(self, urls: list):
        for raw_url in urls:
            if not raw_url:
                continue
            
            cleaned_url = CourlanRouter.validate_and_clean(raw_url)
            if not cleaned_url:
                self._metrics["frontier.trap_dropped"] += 1
                continue
                
            if cleaned_url in self.seen_urls:
                continue
                
            try:
                parsed = urlparse(cleaned_url)
                domain = parsed.netloc.lower()
                if not domain:
                    continue
            except Exception:
                continue
                
            self.seen_urls.add(cleaned_url)
            if domain not in self.domain_buckets:
                self.domain_buckets[domain] = deque()
                self.domain_order.append(domain)
                
            self.domain_buckets[domain].append(cleaned_url)
            self._metrics["frontier.enqueue"] += 1
            
        logger.info(f"Frontier sync complete. Active Domain Queues: {len(self.domain_buckets)} | Seen Register: {len(self.seen_urls)}")

    def dequeue(self) -> str:
        if not self.domain_order:
            return ""
            
        target_domain = self.domain_order[0]
        bucket = self.domain_buckets[target_domain]
        
        url = bucket.popleft()
        self._metrics["frontier.dequeue"] += 1
        
        if not bucket:
            del self.domain_buckets[target_domain]
            self.domain_order.popleft()
        else:
            self.domain_order.rotate(-1)
            
        return url

    def stats(self) -> dict:
        return {
            **self._metrics,
            "queue_depth": sum(len(b) for b in self.domain_buckets.values()),
            "unique_domains_cached": len(self.domain_buckets)
        }

    def flush(self):
        self.domain_buckets.clear()
        self.domain_order.clear()

Frontier = FrontierManager()
