import uuid
import socket
import hashlib
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[NODE-COORDINATOR]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NodeCoordinator")

class ClusterIdentityMatrix:
    @staticmethod
    def construct_immutable_node_signature() -> str:
        print("\n\033[1;32m--- G.O.D. DECENTRALIZED NODE SIGNATURE CALCULATION ---\033[0m")
        try:
            hostname = socket.gethostname()
            mac_int = uuid.getnode()
        except Exception:
            hostname = "fallback_node"
            mac_int = 123456789
            
        raw_seed = f"{hostname}:{mac_int}".encode('utf-8')
        node_sig = hashlib.sha1(raw_seed).hexdigest()[:12].upper()
        
        logger.info(f"Cluster network registration initialized.")
        logger.info(f"  Calculated Local Identity Key: \033[1;32mNODE-X{node_sig}\033[0m")
        return f"NODE-X{node_sig}"

if __name__ == "__main__":
    ClusterIdentityMatrix.construct_immutable_node_signature()
    print("\n\033[1;32m✔ MODULE 56 CLUSTER INDEPENDENT IDENTITY INITIALIZED CONGRUENT.\033[0m\n")
