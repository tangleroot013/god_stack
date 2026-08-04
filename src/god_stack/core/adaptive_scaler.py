#!/usr/bin/env python3
import logging

logger = logging.getLogger("GodStack.AdaptiveScaler")

class AdaptiveScaler:
    def __init__(self, min_workers: int = 1, max_workers: int = 20):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers
        self.success_streak = 0
        self.failure_streak = 0

    def report_success(self) -> int:
        self.failure_streak = 0
        self.success_streak += 1
        
        # Scale up every 5 consecutive successes
        if self.success_streak >= 5 and self.current_workers < self.max_workers:
            self.current_workers += 1
            self.success_streak = 0
            logger.debug(f"Scaling UP: {self.current_workers} workers.")
            
        return self.current_workers

    def report_backpressure(self) -> int:
        self.success_streak = 0
        self.failure_streak += 1
        
        # Scale down rapidly on backpressure
        if self.current_workers > self.min_workers:
            self.current_workers = max(self.min_workers, self.current_workers - 2)
            logger.debug(f"Scaling DOWN: {self.current_workers} workers.")
            
        return self.current_workers
