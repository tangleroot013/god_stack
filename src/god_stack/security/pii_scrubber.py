#!/usr/bin/env python3
import re
import logging

logger = logging.getLogger("GodStack.PIIScrubber")

class PIIScrubber:
    def __init__(self):
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "uuid": re.compile(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', re.IGNORECASE)
        }

    def sanitize_payload(self, text: str) -> str:
        if not text:
            return text
            
        scrubbed = text
        for pii_type, pattern in self.patterns.items():
            scrubbed = pattern.sub(f"[REDACTED_{pii_type.upper()}]", scrubbed)
            
        return scrubbed
