import sys
import types

# ----------------------------------------------------------------------
# Mock prometheus_client
# ----------------------------------------------------------------------
if "prometheus_client" not in sys.modules:
    prom_mock = types.ModuleType("prometheus_client")
    class _NoOpMetric:
        def __init__(self, *a, **kw): pass
        def inc(self, *a, **kw): pass
        def dec(self, *a, **kw): pass
        def set(self, *a, **kw): pass
        def observe(self, *a, **kw): pass
    prom_mock.Counter = _NoOpMetric
    prom_mock.Gauge   = _NoOpMetric
    prom_mock.Summary = _NoOpMetric
    prom_mock.start_http_server = lambda *a, **kw: None
    sys.modules["prometheus_client"] = prom_mock

# ----------------------------------------------------------------------
# Mock websockets (async client)
# ----------------------------------------------------------------------
if "websockets" not in sys.modules:
    ws_mock = types.ModuleType("websockets")
    class _MockWSProtocol:
        async def recv(self): return "{}"
        async def send(self, data): pass
        async def close(self): pass
    async def _mock_connect(*a, **kw):
        return _MockWSProtocol()
    ws_mock.connect = _mock_connect
    sys.modules["websockets"] = ws_mock
