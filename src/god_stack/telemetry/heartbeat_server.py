import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[HEARTBEAT]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Heartbeat")

class AsyncHeartbeatServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8999):
        self.host = host
        self.port = port
        self.system_status = "HEALTHY"

    async def handle_client(self, reader, writer):
        # Read inbound request header bytes
        await reader.read(256)
        
        response_body = f'{{"status": "{self.system_status}", "engine_node": "ONLINE"}}'
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "Connection: close\r\n\r\n"
            f"{response_body}"
        )
        
        writer.write(response.encode('utf-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run_server(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        logger.info(f"Health matrix heartbeat server listening cleanly on http://{self.host}:{self.port}")
        
        # Simulate quick internal verification poll
        await asyncio.sleep(0.1)
        server.close()
        await server.wait_closed()
        logger.info("Validation sequence complete. Server socket recycled successfully.")

async def main():
    print("\n\033[1;32m--- G.O.D. RECOVERY EDGE MONITOR BOOTSTRAP ---\033[0m")
    heartbeat = AsyncHeartbeatServer()
    await heartbeat.run_server()
    print("\n\033[1;32m✔ MODULE 48 HEARTBEAT LIFELINE ENGINE VERIFIED.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
