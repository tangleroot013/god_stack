import asyncio
import json
import logging
import websockets
from websockets import ConnectionClosed

logging.basicConfig(level=logging.INFO, format="\033[1;36m%(asctime)s\033[0m | \033[1;33m[TELEMETRY-RELAY]\033[0m %(message)s")
logger = logging.getLogger("MonitorRelay")

class MonitorRelay:
    """Streams live worker telemetry and throughput to connected dashboards."""
    def __init__(self, host='0.0.0.0', port=8889):
        self.host = host
        self.port = port
        self.clients = set()
        self._server = None

    async def register(self, websocket):
        """Registers a newly connected dashboard client socket."""
        self.clients.add(websocket)
        logger.info(f"🔌 Live HUD Client Connected: {websocket.remote_address}")
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
            logger.info(f"❌ Live HUD Client Disconnected: {websocket.remote_address}")

    async def broadcast(self, event_type: str, data: dict):
        """Dispatches real-time structured events across all active listeners."""
        if not self.clients:
            return

        message = json.dumps({"event": event_type, "payload": data})
        # Use gathering with return_exceptions to ensure bad clients don't drop the engine loop
        await asyncio.gather(
            *[client.send(message) for client in self.clients],
            return_exceptions=True
        )

    async def start(self):
        """Launches the telemetry server bound to the interface context."""
        logger.info(f"📡 Launching Broadcast Stream Server on ws://{self.host}:{self.port}")
        self._server = await websockets.serve(self.register, self.host, self.port)

    async def stop(self):
        """Cleans up sockets safely during stack shutdown sequences."""
        if self._server:
            self._server.close()
            await self._server.wait_closed()
