import os
import socket
import logging

logger = logging.getLogger("GodConfig")

def _determine_metrics_port(default_start: int = 8015) -> int:
    """Safely probes interfaces to resolve a conflict-free metrics port allocation."""
    env_override = os.getenv("GOD_METRICS_PORT")
    if env_override and env_override.isdigit():
        return int(env_override)

    # Search for a clean, open socket boundary slot to eliminate Errno 98
    for port in range(default_start, default_start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Critical Failure: No available network socket slots located for metrics daemon.")

METRICS_PORT = _determine_metrics_port(8015)
