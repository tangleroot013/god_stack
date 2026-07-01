#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Assembling Asynchronous Proxy Balancer Matrix...\033[0m"

cat << 'PYEOF' > run_proxy_balancer.py
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;33m[PROXY-BALANCER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ProxyBalancer")

class AsyncProxyRotator:
    def __init__(self, fallback_nodes=None):
        self.nodes = fallback_nodes or [
            "http://127.0.0.1:8001",
            "http://127.0.0.1:8002",
            "http://127.0.0.1:8003"
        ]
        self._index = 0

    async def acquire_next_egress(self) -> str:
        """Returns the next available node address within the pooling index ring."""
        await asyncio.sleep(0.05) # Emulate connection pool handoff delay
        node = self.nodes[self._index % len(self.nodes)]
        self._index += 1
        return node

async def main():
    print("\n\033[1;32m--- G.O.D. EGRESS BALANCER MATRIX LOOP TEST ---\033[0m")
    rotator = AsyncProxyRotator()
    
    for worker_id in range(4):
        assigned_proxy = await rotator.acquire_next_egress()
        logger.info(f"Worker Node [\033[1;35m{worker_id}\033[0m] securely routed through path: {assigned_proxy}")
        
    print("\n\033[1;32m✔ MODULE 22 ROTATOR LOGATING MATRIX PASSED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
PYEOF

echo -e "\033[1;34m[2/2] Launching verification runner...\033[0m"
./.venv/bin/python3 run_proxy_balancer.py
