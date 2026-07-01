#!/usr/bin/env python3
import json
import csv
import time
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

# --- Advanced HTML Semantic Extractor ---
class SemanticStripper(HTMLParser):
    def __init__(self, target_tag=None, target_attr=None, target_val=None):
        super().__init__()
        self.target_tag = target_tag
        self.target_attr = target_attr
        self.target_val = target_val
        
        self.in_target = False
        self.extracted_text = []
        self.fallback_title = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # Capture title fallback
        if tag == 'title':
            self.in_title = True
        
        # Check specific selector matching
        if self.target_tag and tag == self.target_tag:
            if self.target_attr and attrs_dict.get(self.target_attr) == self.target_val:
                self.in_target = True
            elif not self.target_attr:
                self.in_target = True
        # Heuristic fallback if no rules match
        elif not self.target_tag and tag in ['p', 'article', 'h1']:
            self.in_target = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == self.target_tag or (not self.target_tag and tag in ['p', 'article', 'h1']):
            self.in_target = False

    def handle_data(self, data):
        clean_data = data.strip()
        if not clean_data:
            return
        if self.in_title:
            self.fallback_title = clean_data
        if self.in_target:
            self.extracted_text.append(clean_data)

    def get_data(self):
        title = self.fallback_title if self.fallback_title else "Untitled Target Node"
        summary = " ".join(self.extracted_text[:30]) # Limit length for clean CSV output
        return title, summary if summary else "No indexable content found."

# --- Engine Configuration & Mapping ---
EXTRACTION_SCHEMAS = {
    "en.wikipedia.org": {"tag": "div", "attr": "id", "val": "mw-content-text"},
    "arxiv.org": {"tag": "div", "attr": "id", "val": "abs"},
    "www.nature.com": {"tag": "div", "attr": "class", "val": "c-article-body"}
}

def harvest_node(url):
    domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"
    print(f"[*] Fetching: {url}")
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) god-stack-aggregator/2.0'})
    try:
        with urlopen(req, timeout=5) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
            # Match schema or fall back to generic parser
            schema = EXTRACTION_SCHEMAS.get(domain, {"tag": None, "attr": None, "val": None})
            parser = SemanticStripper(target_tag=schema["tag"], target_attr=schema["attr"], target_val=schema["val"])
            parser.feed(html_content)
            
            title, summary = parser.get_data()
            return {"Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "Source_Domain": domain, "Target_URL": url, "Research_Title": title, "Extracted_Text_Summary": summary[:120] + "...", "Status": "SUCCESS"}
            
    except (URLError, HTTPError) as e:
        print(f"[DLQ] Node quarantine triggered: {url} | Reason: {str(e)}")
        return {"Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "Source_Domain": domain, "Target_URL": url, "Research_Title": "N/A", "Extracted_Text_Summary": f"ERR: Isolation active ({type(e).__name__})", "Status": "QUARANTINED"}

# --- Live Testing Interface ---
if __name__ == "__main__":
    test_targets = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://cluster.example.invalid/dead/endpoint" # Expected quarantine failure
    ]
    
    print("====================================================")
    print("        RUNNING FEATURE 1 TEST SUITE                ")
    print("====================================================")
    
    output_ledger = []
    for target in test_targets:
        res = harvest_node(target)
        output_ledger.append(res)
        
    print("\n[+] Verification Output Matrix:")
    print(json.dumps(output_ledger, indent=2))
