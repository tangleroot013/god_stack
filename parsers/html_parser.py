import re
import logging
from selectolax.parser import HTMLParser

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;35m[HTML-PARSER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("HtmlParser")

# Pre-compile regex matrices at module initialization to completely avoid run-time compilation overhead
RE_TITLE_FALLBACK = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)
RE_CLEAN_WHITESPACE = re.compile(r'\s+')

# Strict protection guard against memory allocation exhaustion vectors
MAX_PAYLOAD_BYTES = 5_000_000  # 5 Megabyte hardware budget allocation ceiling

def parse_html(raw_html: str) -> dict:
    """
    Synchronously extracts target DOM structures from raw HTML strings.
    Leverages selectolax's underlying C-engine implementation for zero-copy efficiency.
    """
    if not raw_html:
        return {"title": None, "body": "", "links": []}

    # Guard against ultra-large data payloads to prevent dynamic GC thrashing
    if len(raw_html) > MAX_PAYLOAD_BYTES:
        logger.warning(f"Payload size ({len(raw_html)} bytes) exceeds processing threshold. Dropping frame.")
        return {"title": "Payload Threshold Abort", "body": "", "links": []}

    # Initialize low-overhead token tree structure
    tree = HTMLParser(raw_html)

    # 1. Structural Title Extraction with Native Engine Fallback
    title_node = tree.css_first('title')
    title = title_node.text().strip() if title_node else None

    if not title:
        match = RE_TITLE_FALLBACK.search(raw_html)
        title = match.group(1).strip() if match else None

    # 2. Optimized Main Document Extraction
    # Target common article/body layouts in a single pass
    content_nodes = tree.css('article, .post-content, .entry-content, main, p')
    body_text = " ".join(node.text().strip() for node in content_nodes if node.text())
    normalized_body = RE_CLEAN_WHITESPACE.sub(" ", body_text).strip()

    # 3. Fast Downstream Link Discovery Discovery Layer
    # Extracts all structural anchors for dynamic Frontier re-enqueuing
    links = []
    for anchor in tree.css('a[href]'):
        href = anchor.attributes.get('href')
        if href:
            clean_href = href.strip()
            if clean_href and not clean_href.startswith(('javascript:', 'mailto:', '#')):
                links.append(clean_href)

    return {
        "title": title,
        "body": normalized_body,
        "links": list(set(links))  # Distinct local frame unique strings
    }
