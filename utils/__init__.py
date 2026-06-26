
# ----------------------------------------------------------------------
# Namespace Compatibility Shim for trailing dot-py import paths
# ----------------------------------------------------------------------
import sys
try:
    import utils.scheduler as _sched
    sys.modules["utils.scheduler.py"] = _sched
except Exception:
    pass

# --- Namespace Compatibility Shim for trailing dot-py import paths ---
import sys
try:
    import utils.scheduler as _sched
    sys.modules["utils.scheduler.py"] = _sched
except Exception:
    pass
