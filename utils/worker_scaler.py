import json
import logging
import mmap
import struct
import time
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("WorkerScaler")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SHM_FILE = PROJECT_ROOT / "vaults" / ".routing_matrix.shm"

# Scaling Policies
DRAIN_ALERT_THRESHOLD = 40.0  # Alert if EMA drain rate drops below this
SUSTAINED_WINDOW_K = 3        # Trigger after K consecutive breaches
COOLDOWN_PERIOD = 10          # Seconds to wait between scale events

class AutoScaler:
    def __init__(self):
        self.breach_counter = 0
        self.last_scale_time = 0
        self.spawned_processes = []

    def _read_shm_state(self):
        if not SHM_FILE.exists():
            return "NOMINAL", 0, []

        try:
            with open(SHM_FILE, "rb") as f:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    # Read Header
                    header = mm[0:16]
                    action_bytes, active_workers = struct.unpack("=12sI", header)
                    global_action = action_bytes.decode('utf-8').strip('\x00')
                    
                    # Read Primary Worker (Worker-00) from Slot 1
                    slot_1 = mm[16:48]
                    w_id, drain_rate, depth, _ = struct.unpack("=12sdId", slot_1)
                    return global_action, active_workers, drain_rate
        except Exception as e:
            return "NOMINAL", 0, 50.0

    def _register_worker_shm(self, worker_id, default_drain=35.0):
        """Atomically appends a new worker slot into the shared memory segment."""
        try:
            with open(SHM_FILE, "r+b") as f:
                with mmap.mmap(f.fileno(), 0) as mm:
                    # Increment worker count in header
                    mm[12:16] = struct.pack("=I", 2)
                    
                    # Write Worker-01 data into Slot 2 (Bytes 48-80)
                    w_bytes = worker_id.encode('utf-8').ljust(12, b'\x00')
                    slot_2_payload = struct.pack("=12sdId", w_bytes, default_drain, 0, time.time())
                    mm[48:80] = slot_2_payload
                    mm.flush()
            logger.info(f"💾 {worker_id} successfully registered in shared memory matrix.")
        except Exception as e:
            logger.error(f"Failed to register worker in SHM: {e}")

    def evaluate_and_scale(self):
        state, worker_count, drain_rate = self._read_shm_state()
        
        if state == "SHED_LOAD" and drain_rate < DRAIN_ALERT_THRESHOLD:
            self.breach_counter += 1
            logger.warning(f"⚠️ Sustained bottleneck detected. Window: {self.breach_counter}/{SUSTAINED_WINDOW_K} (Drain Rate: {drain_rate})")
        else:
            self.breach_counter = max(0, self.breach_counter - 1)

        if self.breach_counter >= SUSTAINED_WINDOW_K:
            current_time = time.time()
            if current_time - self.last_scale_time > COOLDOWN_PERIOD:
                if worker_count < 2:
                    logger.critical("🚀 Scaling Trigger Engaged: Provisioning Worker-01...")
                    
                    # In a production setup, this would trigger k8s/systemd. 
                    # For our pipeline, we spawn a mock worker loop background process.
                    p = subprocess.Popen([sys.executable, "-c", "import time; print('Worker-01 Online'); time.sleep(60)"])
                    self.spawned_processes.append(p)
                    
                    self._register_worker_shm("Worker-01")
                    self.last_scale_time = current_time
                    self.breach_counter = 0
                else:
                    logger.info("ℹ️ Max worker capacity reached for current pool tier.")

    def cleanup(self):
        for p in self.spawned_processes:
            p.terminate()

if __name__ == "__main__":
    scaler = AutoScaler()
    logger.info("🕵️ Worker Scaling Daemon tracking shared memory parameters...")
    try:
        for _ in range(5):  # Run 5 evaluation cycles for simulation loop
            scaler.evaluate_and_scale()
            time.sleep(0.5)
    finally:
        scaler.cleanup()
