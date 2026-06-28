#!/usr/bin/env python3
"""
G.O.D. STACK — PRODUCTION RUNNER DISPATCHER
Architecture: Natively unblocked async orchestration matrix loop.
Integrates live metrics_exporter updates and direct native engine task pools.
Follows pure FOSS principles with independent local task queuing.
"""
import asyncio
import logging
import sys
from metrics_exporter import start_telemetry_server, SYSTEM_METRICS
from orchestrator import GodOrchestrator
from god_engine import GodEngine

# Thread-safe adapter interface to translate thread-offloaded executor requests safely
def patch_god_engine_interface():
    """Maps legacy tracking vectors cleanly into modern async fetch_and_extract engine frames."""
    def process_target_array_patched(self, target_list):
        if not target_list:
            return {"status": "error", "message": "Empty targeting vector array"}
        target_url = target_list[0]
        # Executed inside an isolated thread worker pool; establish an independent runtime loop
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.fetch_and_extract(target_url))
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            loop.close()
            
    GodEngine.process_target_array = process_target_array_patched

# Inject adapter interface path immediately before instantiation sequences
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

    async def bootstrap(self, base_port: int = 8000):
        """Starts the telemetry server with dynamic port fallback and initializes core matrix frameworks."""
        logger.info("Initializing Global Matrix Daemon System Framework...")
        
        # Bind metrics server endpoint context dynamically
        port = base_port
        bound = False
        max_attempts = 5
        
        for attempt in range(max_attempts):
            try:
                start_telemetry_server(port=port)
                bound = True
                break
            except Exception as e:
                logger.warning(f"Port {port} connection busy. Shifting deployment vectors...")
                port += 1
                
        if not bound:
            logger.error("Failed to secure an open telemetry socket endpoint.")
            sys.exit(1)

        # Initialize Core Orchestrator Ecosystem
        await self.orchestrator.initialize_matrix()
        self.active = True
        
        if "god_stack_active_daemons" not in SYSTEM_METRICS:
            SYSTEM_METRICS["god_stack_active_daemons"] = 1
        else:
            SYSTEM_METRICS["god_stack_active_daemons"] += 1

    async def production_loop(self):
        """Drives metrics updates safely across the ingestion pipelines."""
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
    await engine.bootstrap(base_port=8000)
    
    try:
        await engine.production_loop()
    except (KeyboardInterrupt, asyncio.CancelledError):
        engine.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received execution cancellation signal. Matrix shutdown sequence finalized.")
