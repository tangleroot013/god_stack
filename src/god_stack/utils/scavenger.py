#!/usr/bin/env python3
# ==============================================================================
# scavenger.py – Lightweight HTML sanitizer & density calculator
# ==============================================================================
import logging
import re
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;33m%(asctime)s\033[0m | \033[1;35m[SCAVENGER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Scavenger")

class Scavenger:
    def __init__(self):
        self.density_threshold = 0.6

    def sanitize(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "meta", "link"]):
            tag.decompose()
        return str(soup)

    def calculate_density(self, html: str) -> float:
        clean = self.sanitize(html)
        text = re.sub(r"\s+", "", clean)
        total = len(clean)
        if total == 0:
            return 0.0
        return len(text) / total

if __name__ == "__main__":
    scavenger = Scavenger()
    sample = "<html><body><p>Hello world</p></body></html>"
    print(scavenger.sanitize(sample))
    print(f"Density: {scavenger.calculate_density(sample):.2f}")
