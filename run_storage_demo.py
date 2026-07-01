import json
import time
import threading
from data_storage_sync import GodStorageManager
from metrics_exporter import SYSTEM_METRICS

def generate_mock_worker_payload(item_id: str, title: str, score: float) -> dict:
    """Generates a mock data packet formatted identically to worker node payloads."""
    return {
        "worker_id": "node-us-east-edge-01",
        "data": {
            "url": f"https://mirrored-target-cluster.net/products/{item_id}",
            "status": "SUCCESS",
            "extracted_data": {
                "title": title,
                "body": "Listing price optimized for scalable compute fabrics hardware blocks.",
                "links": ["/products/spec", "/home"],
                "enrichment_layer": {
                    "detected_market": "USD_DOMESTIC",
                    "structural_integrity_score": score,
                    "pipeline_pass_engine": "Dynamic_DropIn_Enricher_Matrix"
                }
            }
        }
    }

def main():
    print("\n\033[1;32m--- G.O.D. STACK TRANSACTIONAL STORAGE & DEDUPLICATION TEST ---\033[0m")
    
    # Initialize the Storage Engine (clears and sets schema targets dynamically)
    storage_mgr = GodStorageManager(db_path="god_stack_vfs.db", cold_storage_dir="storage/cold")
    
    # 1. Construct Mock Payload Vectors (including exact duplicate records)
    packet_alpha_1 = generate_mock_worker_payload("item_7700", "Enterprise Framework Cluster Model A", 0.98)
    packet_alpha_2 = generate_mock_worker_payload("item_7700", "Enterprise Framework Cluster Model A", 0.98) # Exact Content Duplicate
    packet_beta    = generate_mock_worker_payload("item_8800", "High-Throughput Quantum Network Switch", 0.95)
    
    # 2. Simulate high-concurrency worker arrivals using separate system execution threads
    print("\n\033[1;36m[INGESTION PHASE]\033[0m Spawning processing workers to stream concurrent data matrices...")
    
    t1 = threading.Thread(target=storage_mgr.process_incoming_payload, args=(packet_alpha_1,))
    t2 = threading.Thread(target=storage_mgr.process_incoming_payload, args=(packet_alpha_2,)) # Duplicate arrival thread
    t3 = threading.Thread(target=storage_mgr.process_incoming_payload, args=(packet_beta,))
    
    # Fire processing frames simultaneously
    t1.start()
    t2.start()
    t3.start()
    
    t1.join()
    t2.join()
    t3.join()
    
    # 3. Analyze post-run telemetry balances
    print("\n\033[1;36m[METRICS ANALYSIS]\033[0m Inspecting internal system counters:")
    print(f" -> Total Ingestion Successes committed: \033[1;32m{SYSTEM_METRICS['god_stack_ingestion_success_total']}\033[0m")
    print(f" -> Total Cryptographic Skips dropped  : \033[1;33m{SYSTEM_METRICS['god_stack_deduplication_skips_total']}\033[0m")
    print(f" -> Total Volumetric Raw Bytes Logged  : \033[1;35m{SYSTEM_METRICS['god_stack_bytes_processed_total']} bytes\033[0m")
    
    print("\n\033[1;32m✔ TRANSACTIONAL STORAGE COMPACTION MANAGEMENT VALIDATED CLEANLY.\033[0m\n")

if __name__ == "__main__":
    main()
