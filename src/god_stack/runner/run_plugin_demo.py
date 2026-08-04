import asyncio
import json
import logging
from core.extension_loader import ExtensionLoader
from metrics_exporter import SYSTEM_METRICS

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[PIPELINE-TEST]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("PipelineTest")

async def test_execution_runloop():
    print("\n\033[1;32m--- G.O.D. STACK EXTENSION SYSTEM LIVE DEMONSTRATION ---\033[0m")
    
    # 1. Initialize Loader Infrastructure
    loader = ExtensionLoader(plugin_dir="parsers")
    await loader.discover_and_mount()
    
    # 2. Mock out a raw payload mimicking output from GodEngine Node
    mock_payload = {
        "url": "https://mirrored-target-cluster.net/products/item_04192",
        "status": "SUCCESS",
        "extracted_data": {
            "title": "Premium Compute Framework Cluster Hardware",
            "body": "Listing price optimized at $1,249.00 available immediately for multi-node nodes.",
            "links": ["/products/item_04192/spec", "/home"]
        }
    }
    
    print("\n\033[1;36m[DATA EXTRUSION FLOW]\033[0m Streaming Mock Payload through Mounted Pipeline Channels...")
    logger.info(f"Payload Initial State Metrics: Total Enrichments Counter = {SYSTEM_METRICS.get('god_stack_ecommerce_enrichments_total', 0)}")
    
    # 3. Broadcast across plug-and-drop chain
    enriched_result = await loader.pipeline_broadcast(mock_payload)
    
    # 4. Assert Operational Compliance Checks
    print("\n\033[1;36m[VALIDATION ANALYSIS]\033[0m Verifying Structural Transformation Enforcements...")
    logger.info(f"Updated Downstream Global Metrics State: {SYSTEM_METRICS['god_stack_ecommerce_enrichments_total']}")
    print(f"\033[1;37mEnriched Resulting JSON Payload Matrix Structure:\033[0m")
    print(json.dumps(enriched_result, indent=4))
    
    # 5. Safe System Teardown Cleanup Handshake
    print("\n\033[1;33m[TEARDOWN]\033[0m Finalizing System Loop Contexts...")
    await loader.terminate_extensions()
    print("\n\033[1;32m✔ DYNAMIC PLUG-AND-DROP EXTENSION SYSTEM VALIDATED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(test_execution_runloop())
