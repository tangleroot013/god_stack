import mmap
import struct
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHM_PATH = PROJECT_ROOT / "vaults" / ".routing_matrix.shm"

SLOT_SIZE = 32
MAX_WORKERS = 8
SHM_SIZE = SLOT_SIZE * MAX_WORKERS
RECORD_FMT = "=12sdB11x"  # Aligned exactly to 32 bytes

def init_shm_space():
    """Allocates a blank aligned memory file structure if missing."""
    SHM_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SHM_PATH.exists() or SHM_PATH.stat().st_size < SHM_SIZE:
        with open(SHM_PATH, "wb") as f:
            f.write(b"\x00" * SHM_SIZE)

def iter_workers():
    """Yields (worker_id, ema_rate, online) fields across allocated slots."""
    if not SHM_PATH.exists():
        return
        
    try:
        with open(SHM_PATH, "rb") as f:
            with mmap.mmap(f.fileno(), SHM_SIZE, access=mmap.ACCESS_READ) as mm:
                for i in range(MAX_WORKERS):
                    offset = i * SLOT_SIZE
                    raw = mm[offset : offset + SLOT_SIZE]
                    
                    wid, rate, status = struct.unpack(RECORD_FMT, raw)
                    wid = wid.rstrip(b"\x00").decode('utf-8', errors='ignore')
                    
                    if not wid:
                        continue
                    yield wid, rate, bool(status)
    except Exception:
        return

def register_worker(worker_id: str, rate: float = 35.0, status: int = 1):
    """Inserts or overwrites a worker entry slot inside the shared memory block."""
    init_shm_space()
    with open(SHM_PATH, "r+b") as f:
        with mmap.mmap(f.fileno(), SHM_SIZE) as mm:
            target_offset = None
            
            for i in range(MAX_WORKERS):
                offset = i * SLOT_SIZE
                wid_bytes = mm[offset : offset + 12]
                existing_id = wid_bytes.rstrip(b"\x00").decode('utf-8', errors='ignore')
                if existing_id == worker_id:
                    target_offset = offset
                    break
            
            if target_offset is None:
                for i in range(MAX_WORKERS):
                    offset = i * SLOT_SIZE
                    wid_bytes = mm[offset : offset + 12]
                    if not wid_bytes.strip(b"\x00"):
                        target_offset = offset
                        break
            
            if target_offset is not None:
                packed = struct.pack(
                    RECORD_FMT, 
                    worker_id.encode('utf-8').ljust(12, b"\x00"), 
                    rate, 
                    status
                )
                mm[target_offset : target_offset + SLOT_SIZE] = packed
                mm.flush()
