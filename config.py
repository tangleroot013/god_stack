import os
import socket
import logging

logger = logging.getLogger(__name__)


def _determine_metrics_port(default_start: int = 8015) -> int:
    """Safely probe local interfaces to resolve a conflict-free metrics port.

    This helper first respects the GOD_METRICS_PORT environment override. If not
    provided, it scans a bounded port range and returns the first bindable port.

    The function is conservative: it will not raise during import time if a
    suitable port cannot be located. Instead it logs a warning and returns the
    provided default_start value. This keeps import-time side effects minimal
    and prevents CI failures caused by unavailable network resources during
    static analysis.
    """
    env_override = os.getenv("GOD_METRICS_PORT")
    if env_override and env_override.isdigit():
        return int(env_override)

    # Search for a clean, open socket boundary slot to eliminate Errno 98
    for port in range(default_start, default_start + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Bind to loopback during detection to avoid reserving a public
                # address during import-time probes.
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue

    logger.warning(
        "No available network socket slots located in range %d-%d; falling back to %d",
        default_start,
        default_start + 99,
        default_start,
    )
    # Fail-safe: return the default start port rather than raising.
    return default_start


# Determine the metrics port at module import time, but do not raise an
# exception if detection fails (keeps CI and static analysis stable).
METRICS_PORT: int = _determine_metrics_port(8015)
