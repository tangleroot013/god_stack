import struct
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("BinaryProcessor")

class WorkerBinaryProcessor:
    def __init__(self):
        # Format specifier: 
        # 12s -> 12-byte char array (worker_id)
        # I   -> unsigned int (high_priority_queue)
        # I   -> unsigned int (standard_queue)
        # f   -> float32 (cpu_utilization)
        self.payload_format = "<12sIIf"
        self.expected_size = struct.calcsize(self.payload_format)

    def pack_payload(self, worker_id: str, high_q: int, std_q: int, cpu_util: float) -> bytes:
        """Serializes tiered queue diagnostics into a packed binary payload string."""
        encoded_id = worker_id.encode('utf-8')[:12].ljust(12, b'\x00')
        return struct.pack(self.payload_format, encoded_id, high_q, std_q, cpu_util)

    def unpack_payload(self, file_path: Path) -> dict:
        """Unpacks the dual-lane structural telemetry format into a Python state matrix."""
        if not file_path.exists():
            return {"status": "MISSING"}
        try:
            raw_bytes = file_path.read_bytes()
            if len(raw_bytes) < self.expected_size:
                return {"status": "CORRUPTED"}
                
            w_id, high_q, std_q, cpu_util = struct.unpack(self.payload_format, raw_bytes[:self.expected_size])
            cleaned_id = w_id.decode('utf-8').rstrip('\x00')
            
            return {
                "status": "VALIDATED",
                "worker_id": cleaned_id,
                "priority_queue_depth": high_q,
                "standard_queue_depth": std_q,
                "queue_depth": high_q + std_q,  # Combined fallback for backward compatibility
                "cpu_utilization_pct": round(cpu_util, 2)
            }
        except Exception as e:
            logger.error(f"Binary parsing anomaly on target {file_path.name}: {e}")
            return {"status": "PARSING_ERROR"}

if __name__ == "__main__":
    # Test generation to simulate severe cluster saturation with mixed priority lanes
    processor = WorkerBinaryProcessor()
    mock_vault = Path(__file__).resolve().parent.parent / "vaults"
    mock_vault.mkdir(parents=True, exist_ok=True)
    
    # 1,420 total items: 120 critical real-time updates, 1300 background ingestions
    packed_data = processor.pack_payload("Worker-00", 120, 1300, 88.50)
    (mock_vault / "worker_00_telemetry.bin").write_bytes(packed_data)
    logger.info("💾 Synthesized dual-lane priority binary payload out to: worker_00_telemetry.bin")
