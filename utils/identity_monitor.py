from collections import defaultdict
import logging

class IdentityHealthMonitor:
    """Tracks the reputation and success velocity of active identity jars."""
    def __init__(self):
        self.stats = defaultdict(lambda: {"success": 0, "blocks": 0, "faults": 0})
        self.logger = logging.getLogger("IdentityMonitor")

    def record_result(self, identity_id: str, status: str):
        """Updates the health matrix for a specific identity footprint."""
        if status == "success":
            self.stats[identity_id]["success"] += 1
        elif status == "block":
            self.stats[identity_id]["blocks"] += 1
        else:
            self.stats[identity_id]["faults"] += 1

    def get_health_payload(self):
        """Formats health metrics for the WebSocket relay."""
        payload = []
        for ident, data in self.stats.items():
            total = sum(data.values())
            success_rate = (data["success"] / total * 100) if total > 0 else 0
            payload.append({
                "id": ident[:8], # Truncated for UI display
                "success_rate": f"{success_rate:.1f}%",
                "blocks": data["blocks"],
                "status": "BURNED" if success_rate < 50 else "HEALTHY"
            })
        return sorted(payload, key=lambda x: x['success_rate'], reverse=True)
