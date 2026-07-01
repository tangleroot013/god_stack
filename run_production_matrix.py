#!/usr/bin/env python3
"""
G.O.D. STACK — PRODUCTION RUNNER DISPATCHER
Architecture: Isolated metrics port framework with explicit global monkeypatching.
"""
import asyncio
import logging
import sys
import socket

# 1. ENFORCE LOW-LEVEL REUSE & REDIRECTION FOR ALL SOCKET BINDINGS
_original_bind = socket.socket.bind
_original_init = socket.socket.__init__

def custom_socket_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    try:
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except Exception:
        pass

def resilient_socket_bind(self, address):
    host, port = address
    # Catch any module (including god_engine/third-party) trying to hijack port 8000
    if port in (8000, 8001, 8011):
        port = 8015
    return _original_bind(self, (host, port))

socket.socket.__init__ = custom_socket_init
socket.socket.bind = resilient_socket_bind

# Proceed with stack module imports safely
import metrics_exporter
from metrics_exporter import start_telemetry_server, SYSTEM_METRICS
from orchestrator import GodOrchestrator
from god_engine import GodEngine

# Hotpatch metrics_exporter function defaults to fully prevent port 8000 utilization
original_start_telemetry = metrics_exporter.start_telemetry_server
def secure_telemetry_fallback(port=8015):
    return original_start_telemetry(port=8015)
metrics_exporter.start_telemetry_server = secure_telemetry_fallback

def patch_god_engine_interface():
    """Maps legacy tracking vectors cleanly into modern async engine frames."""
    def process_target_array_patched(self, target_list):
        if not target_list:
            return {"status": "error", "message": "Empty targeting vector array"}
        target_url = target_list[0]
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.fetch_and_extract(target_url))
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            loop.close()
            
    GodEngine.process_target_array = process_target_array_patched

patch_god_engine_interface()

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;31m[PROD-MATRIX]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ProductionMatrix")

class ProductionMatrixEngine:
    def __init__(self):
        self.orchestrator = GodOrchestrator(use_proxies=False)
        self.active = False
        self._shutdown_event = asyncio.Event()

    async def bootstrap(self, base_port: int = 8015):
        logger.info("Initializing Global Matrix Daemon System Framework...")
        secure_telemetry_fallback(port=base_port)

        await self.orchestrator.initialize_matrix()
        self.active = True
        
        if "god_stack_active_daemons" not in SYSTEM_METRICS:
            SYSTEM_METRICS["god_stack_active_daemons"] = 1
        else:
            SYSTEM_METRICS["god_stack_active_daemons"] += 1

    async def production_loop(self):
        logger.info("Core subsystems active. Entering production daemon loop...")
        
        mock_targets = [
            "https://httpbin.org/html",
            "https://httpbin.org/user-agent"
        ]

        for target in mock_targets:
            if not self.active:
                break

            logger.info(f"Dispatching ingestion job pipeline context for target: {target}")
            SYSTEM_METRICS["god_stack_ingestion_attempts_total"] += 1

            try:
                mission_profile = await self.orchestrator.execute_mission(target)
                if mission_profile.get("status") == "success":
                    logger.info(f"Ingestion mission completed successfully for vector: {target}")
                    SYSTEM_METRICS["god_stack_ingestion_success_total"] += 1
                else:
                    logger.warning(f"Ingestion anomaly caught in pipeline: {mission_profile.get('message')}")
            except Exception as e:
                logger.error(f"Critical execution fault processing target context {target}: {e}")
            
            await asyncio.sleep(2.0)

        await self._shutdown_event.wait()

    def terminate(self):
        logger.info("Deactivating production matrix daemon loop gracefully...")
        self.active = False
        if "god_stack_active_daemons" in SYSTEM_METRICS:
            SYSTEM_METRICS["god_stack_active_daemons"] = max(0, SYSTEM_METRICS["god_stack_active_daemons"] - 1)
        self._shutdown_event.set()

async def main():
    engine = ProductionMatrixEngine()
    await engine.bootstrap(base_port=8015)
    try:
        await engine.production_loop()
    except (KeyboardInterrupt, asyncio.CancelledError):
        engine.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received execution cancellation signal. Matrix shutdown sequence finalized.")
