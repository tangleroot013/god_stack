import asyncio
import logging
from datetime import datetime
from utils.adaptive_throttler import AdaptiveThrottler
from utils.graph_sync import ObsidianGraphSync

# Setup minimal clean stdout logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("SystemCheck")

async def run_diagnostics():
    print("\n=== 🖥️ G.O.D. CLUSTER DIAGNOSTIC TELEMETRY ===")
    
    # 1. Validate Pacing Engine
    throttler = AdaptiveThrottler()
    domain = "api.target-registry.net"
    print(f"\n[+] Testing Adaptive Throttler against target: {domain}")
    
    # Feed mock historical execution speeds (in ms)
    mock_latencies = [420.0, 380.5, 510.2, 460.0]
    for ms in mock_latencies:
        throttler.record_latency(domain, ms)
        
    calculated_delay = throttler.calculate_pacing_delay(domain)
    print(f"    -> Calculated Humanized Delay Window: {calculated_delay}ms")
    
    # 2. Test Markdown Node Telemetry Export
    sync_engine = ObsidianGraphSync()
    mock_identity_payload = {
        "identity_id": "node_alpha_77x",
        "status": "PRISTINE",
        "success_rate": 0.96,
        "total_missions": 142,
        "evaluated_at": datetime.utcnow().isoformat()
    }
    
    print(f"\n[+] Serializing metadata to visual graph...")
    out_path = sync_engine.sync_identity_node(mock_identity_payload)
    print(f"    -> Local vault index created: {out_path}")
    print("\n============================================")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
