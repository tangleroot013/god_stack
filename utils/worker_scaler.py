import os
import sys
import json
import time
import mmap
import struct
import signal
import logging
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.shared_memory import (
    SHM_PATH, SHM_SIZE, SLOT_SIZE, MAX_WORKERS,
    init_shm_space, iter_workers, register_worker
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("MultiLaneWorkerScaler")

CLUSTER_STATE_FILE = PROJECT_ROOT / "vaults" / "cluster_state.json"

# ----- Configuration Thresholds -----
SUSTAINED_WINDOW_K = 3
STABLE_WINDOW_K = 3

# Lane-Specific Scaling Limits
BREACH_THRESHOLD_STANDARD = 1200
BREACH_THRESHOLD_PRIORITY = 300
NOMINAL_THRESHOLD_STANDARD = 400
NOMINAL_THRESHOLD_PRIORITY = 100

IDLE_RATE_MIN = 5.0
COOLDOWN_PERIOD = 2.0             
SCALE_DOWN_COOLDOWN = 2.0         
CHECK_INTERVAL = 0.2

class MultiLaneAutoScaler:
    def __init__(self):
        init_shm_space()
        self.breach_counter = 0
        self.stable_counter = 0
        self.last_scale_time = 0
        self.last_downscale_time = 0
        self.idle_since = {}

    def _get_split_metrics(self):
        if not CLUSTER_STATE_FILE.exists():
            return 0, 0
        try:
            with open(CLUSTER_STATE_FILE, 'r') as f:
                data = json.load(f)
            diagnostics = data.get("worker_diagnostics", {})
            
            total_std_backlog = sum(stats.get("standard_lane_depth", 0) for stats in diagnostics.values())
            total_prio_backlog = sum(stats.get("priority_lane_depth", 0) for stats in diagnostics.values())
            return total_std_backlog, total_prio_backlog
        except:
            return 0, 0

    def _active_workers_count(self):
        return sum(1 for _, _, _, online in iter_workers() if online)

    def unregister_worker(self, worker_id: str):
        with open(SHM_PATH, "r+b") as f:
            with mmap.mmap(f.fileno(), SHM_SIZE) as mm:
                for i in range(MAX_WORKERS):
                    offset = i * SLOT_SIZE
                    wid_bytes = mm[offset : offset + 12]
                    existing_id = wid_bytes.rstrip(b"\x00").decode('utf-8', errors='ignore')
                    if existing_id == worker_id:
                        # Pack empty signature matching structural layout format
                        zeroed = struct.pack("<12s d d B 3x", worker_id.encode('utf-8').ljust(12, b"\x00"), 0.0, 0.0, 0)
                        mm[offset : offset + SLOT_SIZE] = zeroed
                        mm.flush()
                        logger.info(f"🔧 Cleaned shared memory footprint for {worker_id}")
                        return

    def terminate_worker_process(self, worker_id: str):
        try:
            output = subprocess.check_output(["pgrep", "-f", worker_id]).decode().strip()
            for pid_str in output.split("\n"):
                if pid_str:
                    pid = int(pid_str)
                    if pid != os.getpid():
                        os.kill(pid, signal.SIGTERM)
                        logger.info(f"🛑 Dispatched SIGTERM to process PID {pid} ({worker_id})")
        except subprocess.CalledProcessError:
            logger.warning(f"No running process loop discovered for {worker_id}")

    def evaluate_and_scale(self):
        std_backlog, prio_backlog = self._get_split_metrics()
        worker_count = self._active_workers_count()
        current_time = time.time()

        # ----------------- MULTI-LANE BREACH DETECTION (OR Logic) -----------------
        if std_backlog >= BREACH_THRESHOLD_STANDARD or prio_backlog >= BREACH_THRESHOLD_PRIORITY:
            self.breach_counter += 1
            self.stable_counter = 0
            reason = "STANDARD" if std_backlog >= BREACH_THRESHOLD_STANDARD else "PRIORITY"
            logger.warning(f"⚠️ Bottleneck detected via [{reason} LANE]. Window: {self.breach_counter}/{SUSTAINED_WINDOW_K} (Std: {std_backlog}, Prio: {prio_backlog})")
        
        # ----------------- MULTI-LANE CONSOLIDATION DETECTION (AND Logic) -----------------
        elif std_backlog < NOMINAL_THRESHOLD_STANDARD and prio_backlog < NOMINAL_THRESHOLD_PRIORITY:
            self.stable_counter += 1
            self.breach_counter = 0
            if self.stable_counter <= STABLE_WINDOW_K:
                logger.info(f"📉 Cluster nominal state consolidating. Window: {self.stable_counter}/{STABLE_WINDOW_K}")
        else:
            self.breach_counter = max(0, self.breach_counter - 1)
            self.stable_counter = max(0, self.stable_counter - 1)

        # Provisioning Execution Channel
        if self.breach_counter >= SUSTAINED_WINDOW_K:
            if current_time - self.last_scale_time > COOLDOWN_PERIOD:
                if worker_count < 2:
                    logger.critical("🚀 Multi-Lane Scale-Up Engaged: Spawning Worker-01...")
                    subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
                    # Provision split capacity structure: 70% standard, 30% priority split allocation
                    register_worker("Worker-01", std_rate=35.0, prio_rate=15.0, status=1)
                    self.last_scale_time = current_time
                    self.breach_counter = 0
                else:
                    logger.info("ℹ️ Pool matching max capacity constraints.")

        # Teardown Execution Channel
        if self.stable_counter >= STABLE_WINDOW_K:
            if current_time - self.last_downscale_time > SCALE_DOWN_COOLDOWN:
                for wid, std_rate, prio_rate, online in list(iter_workers()):
                    if not online or wid == "Worker-00":  
                        continue
                    
                    # Worker is considered idle if it isn't pulling significant traffic on either lane
                    if std_rate <= IDLE_RATE_MIN and prio_rate <= IDLE_RATE_MIN:
                        self.idle_since.setdefault(wid, current_time)
                    else:
                        self.idle_since.pop(wid, None)

                    if wid in self.idle_since:
                        if worker_count <= 1:
                            logger.info("⚡ Protections active: retaining core master worker instance.")
                            continue

                        logger.critical(f"🔻 Scale-Down Trigger Engaged: De-provisioning {wid}...")
                        self.terminate_worker_process(wid)
                        self.unregister_worker(wid)
                        self.idle_since.pop(wid, None)
                        self.last_downscale_time = current_time
                        self.stable_counter = 0
                        break

if __name__ == "__main__":
    scaler = MultiLaneAutoScaler()
    logger.info("🕵️ Multi-Lane Scaling Daemon monitoring active queue telemetry...")
    try:
        while True:
            scaler.evaluate_and_scale()
            time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Exiting scaler context gracefully.")
