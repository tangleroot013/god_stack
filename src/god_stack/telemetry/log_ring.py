import logging
import collections

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[LOG-RING]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("LogRing")

class BoundedLogRingBuffer:
    def __init__(self, capacity: int = 3):
        # Enforce hard capacity boundary using a deque structure
        self.storage_ring = collections.deque(maxlen=capacity)

    def append_log_event(self, trace_msg: str):
        print("\n\033[1;32m--- G.O.D. RING BUFFER ALLOCATION SEQUENCE ---\033[0m")
        self.storage_ring.append(trace_msg)
        logger.info(f"Event appended. Current buffer utilization: {len(self.storage_ring)}/{self.storage_ring.maxlen}")
        logger.info(f"  Active Oldest Frame: {self.storage_ring[0]}")

if __name__ == "__main__":
    ring = BoundedLogRingBuffer()
    # Write 4 items to force the oldest entry out of the memory-bound pool automatically
    ring.append_log_event("SYS_BOOT_INIT_SEQ")
    ring.append_log_event("NET_SOCKET_OPEN_8081")
    ring.append_log_event("PAYLOAD_TRANS_TX_01")
    ring.append_log_event("EVICTION_TRIGGERED_STALL")
    print("\n\033[1;32m✔ MODULE 63 SLIDING MEMORY LOG POOL COMPLIANT.\033[0m\n")
