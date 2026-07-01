#!/usr/bin/env python3
import urllib.parse
import courlan

class UrlSanitizer:
    @staticmethod
    def normalize(url: str) -> str:
        """Standardizes variant URLs down to a clean, lowercased baseline without tracking tokens."""
        if not url:
            return ""
        
        # Strip outer whitespace to avoid malformed parsing
        url = url.strip()

        # Check prefixes case-insensitively BEFORE checking or prepending standard schemes
        url_lower = url.lower()
        if not url_lower.startswith(("http://", "https://")):
            url = "https://" + url

        # Safely parse the updated URL components
        parsed = urllib.parse.urlparse(url)
        
        # Lowercase the scheme and domain host context explicitly
        url = parsed._replace(
            scheme=parsed.scheme.lower(), 
            netloc=parsed.netloc.lower()
        ).geturl()
        
        # Strip tracking query tags and final fragment hashes
        normalized = courlan.clean_url(url)
        if normalized and "#" in normalized:
            normalized = normalized.split("#")[0]
            
        return normalized
