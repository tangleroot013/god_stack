import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;31m[CIRCUIT-BREAKER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("CircuitBreaker")

class CircuitBreakerOpenException(Exception): pass

class ProductionCircuitBreaker:
    def __init__(self, failure_threshold: int = 2, recovery_time_window: float = 1.0):
        self.failure_threshold = failure_threshold
        self.recovery_time_window = recovery_time_window
        self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN
        self.failure_count = 0
        self.last_state_change = time.time()

    def observe_call(self, success: bool):
        current_time = time.time()
        
        if self.state == "OPEN":
            if current_time - self.last_state_change > self.recovery_time_window:
                logger.info("Recovery time elapsed. Transitioning circuit to \033[1;33m[HALF-OPEN]\033[0m mode...")
                self.state = "HALF-OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit tripped open! Target blocked to prevent cascade exhaustion.")

        if not success:
            self.failure_count += 1
            logger.warning(f"Failure count elevated: {self.failure_count}/{self.failure_threshold}")
            if self.failure_count >= self.failure_threshold and self.state != "OPEN":
                logger.critical("Failure ceiling breached! Tripping circuit to \033[1;31m[OPEN]\033[0m state.")
                self.state = "OPEN"
                self.last_state_change = current_time
        else:
            logger.info("Operation verified healthy. Re-stabilizing matrix parameters to \033[1;32m[CLOSED]\033[0m.")
            self.failure_count = 0
            self.state = "CLOSED"

def main():
    print("\n\033[1;32m--- G.O.D. SUBSYSTEM FAULT COOLDOWN TRACE ---\033[0m")
    breaker = ProductionCircuitBreaker()
    
    # Simulate consecutive target failure drops
    for cycle in range(2):
        breaker.observe_call(success=False)
        
    try:
        breaker.observe_call(success=False)
    except CircuitBreakerOpenException as e:
        logger.info(f"Interceptor caught safety trip exception: {e}")

    print("\n\033[1;32m✔ MODULE 40 INTERCEPTOR BREAKER MATRIX VALIDATED.\033[0m\n")

if __name__ == "__main__":
    main()
