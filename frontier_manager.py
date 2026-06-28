#!/usr/bin/env python3
import logging
from urllib.parse import urlparse
from collections import defaultdict
from url_sanitizer import UrlSanitizer
from courlan_router import CourlanRouter

logger = logging.getLogger("FrontierManager")
logging.basicConfig(level=logging.INFO)

class FrontierManager:
    def __init__(self):
        self.seen_urls = set()
        self.domain_buckets = defaultdict(list)
        self._metrics = {"frontier.enqueue": 0}

    def enqueue_batch(self, urls: list):
        for raw_url in urls:
            if not raw_url:
                continue

            # Full clean pipeline execution sequence: Static -> Engine -> Static (Idempotent lock)
            url = UrlSanitizer.normalize(raw_url)
            cleaned_url = CourlanRouter.validate_and_clean(url)
            if not cleaned_url:
                continue

            final_canonical_url = UrlSanitizer.normalize(cleaned_url)

            # Deduplication safety check
            if final_canonical_url in self.seen_urls:
                continue

            self.seen_urls.add(final_canonical_url)

            # Hash-bucket alignment by lowercased canonical domain context
            domain = urlparse(final_canonical_url).netloc.lower()
            if domain:
                self.domain_buckets[domain].append(final_canonical_url)
                self._metrics["frontier.enqueue"] += 1

        logger.info(f"Frontier sync complete. Active Domain Queues: {len(self.domain_buckets)} | Seen Register: {len(self.seen_urls)}")

    def dequeue(self) -> str:
        for domain, queue in self.domain_buckets.items():
            if queue:
                return queue.pop(0)
        return ""

    def stats(self) -> dict:
        return self._metrics

    def flush(self):
        self.seen_urls.clear()
        self.domain_buckets.clear()
        self._metrics["frontier.enqueue"] = 0

# Legacy compatibility alias for downstream scrapers
Frontier = FrontierManager
