#!/usr/bin/env python3
import json
import time
from itertools import cycle
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

class ProxyCircuitBreaker:
    def __init__(self, proxy_list):
        """Initializes a thread-safe cyclic proxy pool."""
        self.proxy_pool = cycle(proxy_list) if proxy_list else None
        self.active_proxy = None

    def rotate_gateway(self):
        """Switches the active outbound interface pathway."""
        if self.proxy_pool:
            self.active_proxy = next(self.proxy_pool)
        else:
            self.active_proxy = "DIRECT_CONNECT"
        return self.active_proxy

def harvest_with_proxy(url, proxy_manager):
    domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"
    gateway = proxy_manager.rotate_gateway()
    
    print(f"[*] Route: [{gateway}] ──► Fetching: {url}")
    
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 god-stack-aggregator/2.0'})
    
    # Pure Python implementation of proxy injection via urllib
    if gateway != "DIRECT_CONNECT" and not gateway.startswith("MOCK_"):
        req.set_proxy(gateway, 'http')

    try:
        # Simulate network delay variations
        time.sleep(0.2)
        
        # Guardrail check against simulated offline proxies
        if "OFFLINE" in gateway:
            raise URLError(f"Proxy Connection Refused: {gateway}")
            
        with urlopen(req, timeout=3) as response:
            return {
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Target_URL": url,
                "Outbound_Gateway": gateway,
                "Status": "SUCCESS"
            }
            
    except (URLError, HTTPError) as e:
        print(f"[DLQ] Gateway Fault Intercepted on [{gateway}] | Reason: {str(e)}")
        return {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Target_URL": url,
            "Outbound_Gateway": gateway,
            "Status": "QUARANTINED"
        }

if __name__ == "__main__":
    # Define a mix of direct, mock working, and dead mock proxies for tracking verification
    sample_proxies = [
        "DIRECT_CONNECT",
        "MOCK_PROXY_NODE_01:8080",
        "MOCK_PROXY_OFFLINE_02:3128",
        "MOCK_PROXY_NODE_03:8080"
    ]
    
    test_targets = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://arxiv.org/list/cs.AI/recent",
        "https://www.nature.com/articles/d41586-026-00123-x",
        "https://en.wikipedia.org/wiki/Open-source_software"
    ]
    
    manager = ProxyCircuitBreaker(sample_proxies)
    
    print("====================================================")
    print("        RUNNING FEATURE 2 TEST SUITE                ")
    print("====================================================")
    
    output_ledger = []
    for target in test_targets:
        res = harvest_with_proxy(target, manager)
        output_ledger.append(res)
        
    print("\n[+] Verification Proxy Matrix Summary:")
    print(json.dumps(output_ledger, indent=2))
