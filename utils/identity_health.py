import logging
import json
from datetime import datetime
from collections import defaultdict
from typing import Dict, Optional

log = logging.getLogger("IdentityHealthMonitor")

class IdentityHealthMonitor:
    """Tracks, grades, and quarantines identity jars based on behavioral telemetry."""
    
    def __init__(self, redis_client=None, critical_threshold: float = 0.75):
        self.redis = redis_client
        self.critical_threshold = critical_threshold
        self.local_registry: Dict[str, Dict] = defaultdict(lambda: {"successes": 0, "total": 0, "status": "PRISTINE"})

    async def record_mission_outcome(self, identity_id: str, success: bool) -> Dict:
        """Updates the statistical reliability index for a specific identity jar."""
        if self.redis:
            redis_key = f"god_stack:identity_health:{identity_id}"
            pipe = self.redis.pipeline()
            pipe.hincrby(redis_key, "total", 1)
            if success:
                pipe.hincrby(redis_key, "successes", 1)
            results = await pipe.execute()
            
            successes = int(results[1] if success else await self.redis.hget(redis_key, "successes") or 0)
            total = int(results[0])
        else:
            self.local_registry[identity_id]["total"] += 1
            if success:
                self.local_registry[identity_id]["successes"] += 1
            successes = self.local_registry[identity_id]["successes"]
            total = self.local_registry[identity_id]["total"]

        success_rate = successes / total if total > 0 else 1.0
        status = "PRISTINE" if success_rate >= 0.90 else "DEGRADED" if success_rate >= self.critical_threshold else "QUARANTINED"

        health_payload = {
            "identity_id": identity_id,
            "success_rate": round(success_rate, 2),
            "total_missions": total,
            "status": status,
            "evaluated_at": datetime.utcnow().isoformat() + "Z"
        }

        if self.redis:
            await self.redis.hset(f"god_stack:identity_health:{identity_id}", "status", status)
            if status == "QUARANTINED":
                await self.redis.sadd("god_stack:quarantine_set", identity_id)
        else:
            self.local_registry[identity_id]["status"] = status

        log.info(f"📊 Identity {identity_id} metrics evaluated: {status} ({success_rate*100:.1f}% accuracy)")
        return health_payload
