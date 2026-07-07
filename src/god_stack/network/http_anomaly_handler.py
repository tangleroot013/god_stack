#!/usr/bin/env python3
import random
import logging
from typing import Dict, Any

logger = logging.getLogger("GodStack.HttpAnomalyHandler")

class HttpAnomalyHandler:
    def __init__(self, base_backoff: float = 1.0, max_backoff: float = 60.0):
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff

    def evaluate_status(self, status_code: int, current_retry_attempt: int) -> Dict[str, Any]:
        result = {"action": "PROCEED", "suggested_delay": 0.0}
        
        if status_code == 200:
            return result
            
        # Severe rate limits or target defensive posture
        if status_code in (429, 403):
            factor = 2.5 ** current_retry_attempt
            delay = min(self.max_backoff, self.base_backoff * factor)
            jitter = random.uniform(0.5, 1.5) * delay
            result.update({"action": "QUARANTINE_AND_BACKOFF", "suggested_delay": jitter})
            logger.warning(f"Defensive status caught [{status_code}]. Escalating delay vector to {jitter:.2f}s.")
            
        # Node errors or target infrastructure strain
        elif status_code in (500, 502, 503, 504):
            factor = 2.0 ** current_retry_attempt
            delay = min(self.max_backoff, self.base_backoff * factor)
            jitter = random.uniform(0.8, 1.2) * delay
            result.update({"action": "RETRY_WITH_JITTER", "suggested_delay": jitter})
            logger.info(f"Infrastructure fault caught [{status_code}]. Executing dynamic sleep for {jitter:.2f}s.")
            
        else:
            result.update({"action": "ABORT_PIPELINE"})
            logger.error(f"Terminal connection structural error code: {status_code}.")
            
        return result
