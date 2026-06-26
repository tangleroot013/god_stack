import pytest
from aiohttp import web
from daemon_core import DaemonCore

@pytest.mark.asyncio
async def test_health_endpoint_response_format(aiohttp_client):
    core = DaemonCore()
    client = await aiohttp_client(core.app)
    
    resp = await client.get('/healthz')
    assert resp.status == 200
    
    data = await resp.json()
    assert "status" in data
    assert "redis" in data
    assert "workers_pooled" in data
