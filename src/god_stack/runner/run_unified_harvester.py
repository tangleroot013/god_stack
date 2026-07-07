#!/usr/bin/env python3
import csv
import json
import time
import random
import threading
from itertools import cycle
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

# --- 1. HTML DOM Selector Engine ---
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
        if tag == 'title':
            self.in_title = True
        if self.target_tag and tag == self.target_tag:
            if self.target_attr and attrs_dict.get(self.target_attr) == self.target_val:
                self.in_target = True
            elif not self.target_attr:
                self.in_target = True
        elif not self.target_tag and tag in ['p', 'article']:
            self.in_target = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        if tag == self.target_tag or (not self.target_tag and tag in ['p', 'article']):
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
        title = self.fallback_title if self.fallback_title else "Untitled Node"
        summary = " ".join(self.extracted_text[:25])
        return title, summary if summary else "No layout contents found."

# --- 2. Adaptive System Components ---
class UnifiedOrchestrator:
    def __init__(self, proxies, base_delay=0.2, output_csv="unified_research_ledger.csv"):
        self.output_csv = Path(output_csv)
        self.csv_lock = threading.Lock()
        self.proxy_pool = cycle(proxies) if proxies else None
        
        # Rate limiting state
        self.base_delay = base_delay
        self.domain_penalties = {}
        self.throttle_lock = threading.Lock()

        # Domain Target Mappings
        self.schemas = {
            "en.wikipedia.org": {"tag": "div", "attr": "id", "val": "mw-content-text"},
            "arxiv.org": {"tag": "div", "attr": "id", "val": "abs"},
            "www.nature.com": {"tag": "div", "attr": "class", "val": "c-article-body"}
        }
        
        self.fields = ["Timestamp", "Thread_ID", "Outbound_Gateway", "Target_URL", "Research_Title", "Summary", "Status"]
        self.initialize_csv()

    def initialize_csv(self):
        with self.csv_lock:
            with open(self.output_csv, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writeheader()

    def get_route_and_delay(self, domain):
        """Thread-safe acquisition of gateway and dynamic adaptive delay parameters."""
        gateway = next(self.proxy_pool) if self.proxy_pool else "DIRECT_CONNECT"
        
        with self.throttle_lock:
            penalty = self.domain_penalties.get(domain, 0.0)
            
        calculated_delay = self.base_delay + penalty + random.uniform(0.1, 0.3)
        return gateway, calculated_delay

    def flag_rate_limit(self, domain):
        with self.throttle_lock:
            current = self.domain_penalties.get(domain, 0.0)
            self.domain_penalties[domain] = current + 2.5
            print(f"[THROTTLE] Penalty scaled for {domain} -> +2.5s backoff.")

    def harvest_worker(self, url):
        thread_id = f"Worker-{threading.get_ident()}"
        domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"
        
        gateway, delay = self.get_route_and_delay(domain)
        time.sleep(delay)
        
        # Error simulation rules to prove resilience
        if "rate-limit" in url:
            self.flag_rate_limit(domain)
            return self.commit_row(thread_id, gateway, url, "N/A", "429 Rate Limit Sim Boundary Triggered", "RATE_LIMITED")
        if "offline-proxy" in gateway:
            return self.commit_row(thread_id, gateway, url, "N/A", "ERR: Proxy Routing Fault Intercepted", "QUARANTINED")

        # Live Web Request Execution
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 god-stack-aggregator/4.0'})
        if gateway != "DIRECT_CONNECT" and not gateway.startswith("MOCK_"):
            req.set_proxy(gateway, 'http')

        try:
            with urlopen(req, timeout=4) as response:
                html = response.read().decode('utf-8', errors='ignore')
                schema = self.schemas.get(domain, {"tag": None, "attr": None, "val": None})
                
                parser = SemanticStripper(target_tag=schema["tag"], target_attr=schema["attr"], target_val=schema["val"])
                parser.feed(html)
                title, summary = parser.get_data()
                
                return self.commit_row(thread_id, gateway, url, title, summary[:90] + "...", "SUCCESS")
        except Exception as e:
            return self.commit_row(thread_id, gateway, url, "N/A", f"Exception Caught: {type(e).__name__}", "QUARANTINED")

    def commit_row(self, thread_id, gateway, url, title, summary, status):
        row = {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Thread_ID": thread_id,
            "Outbound_Gateway": gateway,
            "Target_URL": url,
            "Research_Title": title,
            "Summary": summary,
            "Status": status
        }
        with self.csv_lock:
            with open(self.output_csv, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fields)
                writer.writerow(row)
        return row

# --- 3. Parallel Batch Orchestration Run ---
if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor, as_completed

    proxies = ["DIRECT_CONNECT", "MOCK_PROXY_NODE_01:8080", "MOCK_PROXY_offline-proxy_02:3128"]
    targets = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://rate-limit-site.invalid/research/node1",
        "https://arxiv.org/list/cs.AI/recent",
        "https://www.nature.com/articles/d41586-026-00123-x",
        "https://en.wikipedia.org/wiki/Open-source_software"
    ]

    orchestrator = UnifiedOrchestrator(proxies=proxies, base_delay=0.1)
    
    print("====================================================")
    print("      LAUNCHING UNIFIED HIGH-THROUGHPUT HARVESTER    ")
    print("====================================================\n")
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(orchestrator.harvest_worker, url) for url in targets]
        for future in as_completed(futures):
            res = future.result()
            print(f"[FLUSH] URL: {res['Target_URL']} -> [{res['Status']}]")

    print("\n====================================================")
    print("RUN COMPLETE. Data ledger successfully generated.")
    print("====================================================")
