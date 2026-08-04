import mmap
import struct
import logging
from pathlib import Path

logger = logging.getLogger("SharedMemory")

# 32-byte layout: 12-byte ID, 8-byte std_rate, 8-byte prio_rate, 1-byte status, 3-byte padding
RECORD_FMT = "<12s d d B 3x"
SLOT_SIZE = 32
MAX_WORKERS = 8
SHM_SIZE = SLOT_SIZE * MAX_WORKERS
SHM_PATH = Path("vaults/.routing_matrix.shm")

def init_shm_space():
    SHM_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not SHM_PATH.exists() or SHM_PATH.stat().st_size != SHM_SIZE:
        with open(SHM_PATH, "wb") as f:
            f.write(b"\x00" * SHM_SIZE)
        logger.info("Initialized a clean split-lane shared memory block.")

def register_worker(worker_id: str, std_rate: float = 35.0, prio_rate: float = 35.0, status: int = 1):
    init_shm_space()
    with open(SHM_PATH, "r+b") as f:
        with mmap.mmap(f.fileno(), SHM_SIZE) as mm:
            target_offset = None

            # Pass 1: Scan for identity overwrite
            for i in range(MAX_WORKERS):
                offset = i * SLOT_SIZE
                wid_bytes = mm[offset : offset + 12]
                existing_id = wid_bytes.rstrip(b"\x00").decode('utf-8', errors='ignore')
                if existing_id == worker_id:
                    target_offset = offset
                    break

            # Pass 2: Scan for unallocated block space
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
                    std_rate,
                    prio_rate,
                    status
                )
                mm[target_offset : target_offset + SLOT_SIZE] = packed
                mm.flush()

def iter_workers():
    init_shm_space()
    with open(SHM_PATH, "rb") as f:
        with mmap.mmap(f.fileno(), SHM_SIZE, access=mmap.ACCESS_READ) as mm:
            for i in range(MAX_WORKERS):
                offset = i * SLOT_SIZE
                raw = mm[offset : offset + SLOT_SIZE]
                wid_bytes, std_rate, prio_rate, status = struct.unpack(RECORD_FMT, raw)
                worker_id = wid_bytes.rstrip(b"\x00").decode('utf-8', errors='ignore')
                if not worker_id:
                    continue
                yield worker_id, std_rate, prio_rate, bool(status)
