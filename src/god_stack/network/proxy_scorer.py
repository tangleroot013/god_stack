import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[PROXY-SCORER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ProxyScorer")

class ProxyPerformanceScorer:
    def __init__(self):
        self.proxy_scores = {}

    def log_egress_transaction(self, proxy_ip: str, execution_success: bool):
        print("\n\033[1;32m--- G.O.D. EGRESS CONNECTOR PERFORMANCE MATRIX ---\033[0m")
        current_score = self.proxy_scores.get(proxy_ip, 100)
        
        if execution_success:
            # Gradually reward stable connection nodes
            new_score = min(100, current_score + 5)
            logger.info(f"Connection verification successful for [ \033[1;32m{proxy_ip}\033[0m ]")
        else:
            # Heavily penalize dropped pipeline frames
            new_score = max(0, current_score - 30)
            logger.warning(f"Connection fault detected on endpoint channel [ \033[1;31m{proxy_ip}\033[0m ]")
            
        self.proxy_scores[proxy_ip] = new_score
        logger.info(f"  Updated Node Quality Coefficient: \033[1;34m{new_score}/100\033[0m")

if __name__ == "__main__":
    scorer = ProxyPerformanceScorer()
    scorer.log_egress_transaction("192.168.42.10", execution_success=True)
    scorer.log_egress_transaction("192.168.42.11", execution_success=False)
    print("\n\033[1;32m✔ MODULE 90 PROXY TRANSIT ROUTING INDEX ONLINE.\033[0m\n")
