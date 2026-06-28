#!/usr/bin/env python3
import pytest
from courlan_router import CourlanRouter
from url_sanitizer import UrlSanitizer
from frontier_manager import FrontierManager

@pytest.mark.parametrize(
    "raw_url,expected_canonical",
    [
        ("HTTPS://NEWS.YCOMBINATOR.COM/item?id=45&utm_source=twitter&fbclid=xyz123#hash", "https://news.ycombinator.com/item?id=45"),
        ("http://news.ycombinator.com/front?fbclid=abc567#comments-section", "https://news.ycombinator.com/front"),
    ],
)
def test_end_to_end_pipeline_normalization(raw_url, expected_canonical):
    """Confirms that the complete ingress path produces uniform outputs independent of input contamination."""
    # Test Router Boundary
    router_cleaned = CourlanRouter.validate_and_clean(raw_url)
    assert router_cleaned != ""
    
    # Test Frontier Normalization Identity
    final_output = UrlSanitizer.normalize(router_cleaned)
    assert final_output == expected_canonical

def test_frontier_deduplication_engine():
    """Validates that distinct dirty variations of an identical target do not bypass queue filters."""
    frontier = FrontierManager()
    dirty_matrix = [
        "HTTPS://NEWS.YCOMBINATOR.COM/item?id=99&utm_source=newsletter",
        "https://news.ycombinator.com/item?id=99&fbclid=xyz999#main-content",
        "news.ycombinator.com/item?id=99"
    ]
    
    frontier.enqueue_batch(dirty_matrix)
    
    # Verify exactly 1 target was enqueued despite structural discrepancies
    assert len(frontier.seen_urls) == 1
    assert frontier.stats()["frontier.enqueue"] == 1
