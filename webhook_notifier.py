#!/usr/bin/env python3
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

class WebhookNotifier:
    def __init__(self, webhook_url=None):
        # Fallback to an environment variable if not passed directly
        self.webhook_url = webhook_url

    def dispatch_alert(self, node_url, error_context):
        """Sends a structured JSON alert payload to your monitoring channel."""
        if not self.webhook_url:
            print("\033[1;33m[WARN] Webhook URL not configured. Alert suppressed.\033[0m")
            return False

        # Structured layout compatible with Discord embeds / Slack blocks
        payload = {
            "username": "G.O.D. STACK MONITOR",
            "content": f"⚠️ **CRITICAL EXTRACTION FAULT DETECTED** ⚠️",
            "embeds": [{
                "title": "Ingestion Pipeline Interruption",
                "color": 16724787, # Red
                "fields": [
                    {"name": "Target Node URL", "value": f"`{node_url}`", "inline": False},
                    {"name": "Error Context", "value": f"*{error_context}*", "inline": False}
                ]
            }]
        }

        try:
            req = Request(
                self.webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "GodStack-Monitor"}
            )
            with urlopen(req) as response:
                if response.status in [200, 204]:
                    print("\033[0;32m[NOTIFIER] Operational alert sent successfully.\033[0m")
                    return True
        except URLError as net_err:
            print(f"\033[0;31m[NOTIFIER ERROR] Failed to deliver alert payload: {net_err.reason}\033[0m")
        except Exception as e:
            print(f"\033[0;31m[NOTIFIER ERROR] Unexpected exception: {e}\033[0m")
        return False

if __name__ == "__main__":
    # Test pass with an unconfigured URL to verify structural safety
    notifier = WebhookNotifier(webhook_url=None)
    notifier.dispatch_alert("https://example.com/faulty_node", "403 Forbidden - Shield Blocked")
