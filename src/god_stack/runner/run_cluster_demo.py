import asyncio
import logging
from api.mock_coordinator import start_coordinator_server
from worker_node import GodWorkerNode

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[CLUSTER-RUNNER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ClusterRunner")

async def main():
    print("\n\033[1;32m--- G.O.D. STACK DISTRIBUTED COMPUTING GRID DEMONSTRATION ---\033[0m")
    
    # 1. Start standard library mock cluster master server
    coordinator_port = 8999
    server = start_coordinator_server(port=coordinator_port)
    
    # 2. Instantiate and connect decentralized worker instances
    master_endpoint = f"http://127.0.0.1:{coordinator_port}"
    worker = GodWorkerNode(master_url=master_endpoint, concurrency_limit=2)
    
    try:
        # Run the primary polling consumption loop until test URLs are fully consumed
        await worker.run_worker_loop()
    finally:
        # 3. Handle resource and background server context cleanups
        await worker.shutdown()
        server.shutdown()
        server.server_close()
        print("\n\033[1;32m✔ DECENTRALIZED MULTI-NODE SWARM WORKSPACE SYNCHRONIZED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
