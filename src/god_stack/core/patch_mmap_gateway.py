#!/usr/bin/env python3
from url_sanitizer import UrlSanitizer

class MMapBuffer:
    def __init__(self):
        self.payload = bytearray()

class Gateway:
    def __init__(self):
        self._buffers = {}

    def get_buffer_for(self, url: str) -> MMapBuffer:
        """Retrieves or instantiates unique memory-mapped allocation blocks keyed by canonical URL context."""
        if not url:
            return None
        key = UrlSanitizer.normalize(url)
        return self._buffers.setdefault(key, MMapBuffer())
