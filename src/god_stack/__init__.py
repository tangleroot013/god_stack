"""G.O.D. Stack — Global Orchestration Daemon Stack

A resilient, distributed engine framework for high-frequency daemon clustering,
stealth-profile URL routing, Prometheus telemetry, and live observability via Grafana.
"""

__version__ = "2.2.0"
__author__ = "tangleroot013"

# Core exports
from god_stack.core.god_engine import GodEngine
from god_stack.core.daemon_core import DaemonCore

__all__ = [
    "GodEngine",
    "DaemonCore",
    "__version__",
]
