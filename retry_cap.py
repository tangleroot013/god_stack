import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[RETRY-CAP]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("RetryCap")

class OutboundConnectionRetryCap:
    def __init__(self, max_allowed_attempts: int = 3):
        self.max_attempts = max_allowed_attempts

    def evaluate_retry_state(self, current_retry_count: int, route_id: str) -> bool:
        print("\n\033[1;32m--- G.O.D. FAULT TOLERANCE BOUNDARY TRACKING ---\033[0m")
        logger.info(f"Evaluating delivery persistence index for pipeline route: [ {route_id} ]")
        
        if current_retry_count >= self.max_attempts:
            logger.critical(f"  \033[1;31mRETRY MAXIMUM EXCEEDED!\033[0m Hard-capping path [ {route_id} ] at {current_retry_count} iterations.")
            logger.warning("  Action: Deflecting dead execution track to failure recovery partition.")
            return False
            
        logger.info(f"  Route safety margin cleared. Current: {current_retry_count}/{self.max_attempts}. Proceeding with next check.")
        return True

if __name__ == "__main__":
    capper = OutboundConnectionRetryCap()
    capper.evaluate_retry_state(current_retry_count=1, route_id="EGRESS_NODE_ALPHA")
    capper.evaluate_retry_state(current_retry_count=3, route_id="EGRESS_NODE_OMEGA")
    print("\n\033[1;32m✔ MODULE 96 RETRY BOUNDARY HARD-CAPS COMPLETE.\033[0m\n")
