import sys
import types
import importlib

# Keep a reference to the actual websockets package module
try:
    # Temporarily remove mock mapping if it exists to fetch the real package
    real_ws_meta = sys.modules.pop("websockets", None)
    real_websockets = importlib.import_module("websockets")
finally:
    if real_ws_meta:
        sys.modules["websockets"] = real_ws_meta

class DynamicMockPackage(types.ModuleType):
    def __getattr__(self, name):
        # Fallback to the real package implementations for live properties (like .serve or .connect)
        return getattr(real_websockets, name)

ws_mock = DynamicMockPackage("websockets")
ws_mock.__path__ = []

# Mock exceptions interface specifically for unit isolation layers
exceptions_mock = types.ModuleType("websockets.exceptions")
class ConnectionClosed(Exception): pass
exceptions_mock.ConnectionClosed = ConnectionClosed

ws_mock.exceptions = exceptions_mock
sys.modules["websockets.exceptions"] = exceptions_mock
sys.modules["websockets"] = ws_mock
