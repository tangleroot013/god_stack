#!/usr/bin/env python3
import json
import time
import random
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

class AdaptiveThrottler:
    def __init__(self, base_delay=0.2):
        self.base_delay = base_delay
        self.domain_penalties = {}

    def get_delay(self, domain):
        """Calculates current dynamic delay including accumulated penalties."""
        penalty = self.domain_penalties.get(domain, 0.0)
        jitter = random.uniform(0.1, 0.4)
        return self.base_delay + penalty + jitter

    def flag_rate_limit(self, domain, retry_after=None):
        """Applies an incremental structural penalty weight to the domain."""
        added_penalty = float(retry_after) if retry_after else 2.0
        current = self.domain_penalties.get(domain, 0.0)
        self.domain_penalties[domain] = current + added_penalty
        print(f"[THROTTLE] Penalty applied to {domain}: +{added_penalty}s backoff weight.")

    def cool_down(self, domain):
        """Gradually decays penalties for successful responses."""
        if domain in self.domain_penalties:
            current = self.domain_penalties[domain]
            if current > 0.5:
                self.domain_penalties[domain] = current - 0.5
            else:
                self.domain_penalties.pop(domain, None)

def harvest_with_backoff(url, throttler):
    domain = url.split("//")[-1].split("/")[0] if "//" in url else "unknown_host"
    
    calculated_delay = throttler.get_delay(domain)
    print(f"[*] Throttler calculated delay for {domain}: {calculated_delay:.2f}s")
    time.sleep(calculated_delay)
    
    print(f"[*] Requesting: {url}")
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0 god-stack-aggregator/3.0'})
    
    try:
        # Simulate an unexpected 429 Rate Limit block on specific targets
        if "rate-limited-site" in url:
            # Simulate a standard HTTPError container object
            raise HTTPError(url, 429, "Too Many Requests", {"Retry-After": "3"}, None)
            
        with urlopen(req, timeout=3) as response:
            throttler.cool_down(domain)
            return {
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Target_URL": url,
                "Delay_Applied": f"{calculated_delay:.2f}s",
                "Status": "SUCCESS"
            }
            
    except HTTPError as e:
        if e.code == 429:
            retry_after = e.headers.get("Retry-After")
            print(f"[!] Target triggered 429 rate limit payload boundary.")
            throttler.flag_rate_limit(domain, retry_after)
            return {
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Target_URL": url,
                "Delay_Applied": f"{calculated_delay:.2f}s",
                "Status": "RATE_LIMITED_RETRY"
            }
        else:
            return {
                "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Target_URL": url,
                "Delay_Applied": f"{calculated_delay:.2f}s",
                "Status": "FAILED"
            }
    except URLError:
        return {
            "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Target_URL": url,
            "Delay_Applied": f"{calculated_delay:.2f}s",
            "Status": "QUARANTINED"
        }

if __name__ == "__main__":
    throttler = AdaptiveThrottler(base_delay=0.1)
    
    test_targets = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://rate-limited-site.org/api/v1/research", # First hit triggers 429
        "https://rate-limited-site.org/api/v2/research", # Second hit adapts with safety backoff delay
        "https://en.wikipedia.org/wiki/Open-source_software"
    ]
    
    print("====================================================")
    print("        RUNNING FEATURE 3 TEST SUITE                ")
    print("====================================================")
    
    output_ledger = []
    for target in test_targets:
        res = harvest_with_backoff(target, throttler)
        output_ledger.append(res)
        
    print("\n[+] Verification Rate-Limit Intelligence Matrix:")
    print(json.dumps(output_ledger, indent=2))
