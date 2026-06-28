import pytest
import asyncio
import websockets
from websockets import ConnectionClosed
from utils.monitor_relay import MonitorRelay
from daemon_core import DaemonCore

@pytest.mark.asyncio
async def test_websocket_broadcast_lifecycle():
    # Spin up relay server on a non-standard testing port
    relay = MonitorRelay(host="127.0.0.1", port=8999)
    await relay.start()

    async def dummy_coro():
        return {"scraped_nodes": 42}

    daemon = DaemonCore(monitor_relay=relay)

    # Listen to stream simultaneously using an internal client socket connection
    async with websockets.connect("ws://127.0.0.1:8999") as client:
        # Trigger daemon job loop
        job_task = asyncio.create_task(daemon.run_job("Specialist-01", dummy_coro()))
        
        # Capture raw telemetry frame
        msg_start = await client.recv()
        msg_success = await client.recv()
        await job_task

    await relay.stop()

    assert "worker_start" in msg_start
    assert "worker_success" in msg_success
    assert "Specialist-01" in msg_success
