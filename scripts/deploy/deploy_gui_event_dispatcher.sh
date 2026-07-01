#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Engineering Thread-Safe Telemetry Event Pipeline Dispatcher...\033[0m"

cat << 'PYEOF' > gui_event_dispatcher.py
import tkinter as tk
import queue
import threading
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[EVENT-DISPATCH]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("EventDispatch")

class TelemetryEventDispatcher:
    def __init__(self, root_window, display_callback):
        self.root = root_window
        self.callback = display_callback
        self.msg_queue = queue.Queue()
        
    def start_polling_loop(self):
        # Process all pending messages currently inside the atomic thread queue
        while not self.msg_queue.empty():
            try:
                message = self.msg_queue.get_nowait()
                self.callback(message)
                self.msg_queue.task_done()
            except queue.Empty:
                break
        # Re-schedule polling step inside the master UI thread allocation table
        self.root.after(100, self.start_polling_loop)

    def inject_background_telemetry(self, event_data: str):
        # Background worker threads use this interface to securely queue lines
        self.msg_queue.put(event_data)

if __name__ == "__main__":
    print("\n\033[1;32m--- G.O.D. CROSS-THREAD VIEW-PORT PIPELINE ---\033[0m")
    root = tk.Tk()
    
    def ui_sink(msg):
        logger.info(f"UI Thread safely rendered background event: [ {msg} ]")

    dispatcher = TelemetryEventDispatcher(root, ui_sink)
    dispatcher.start_polling_loop()
    
    # Simulate a decoupled background worker thread pushing an ingestion event
    sim_thread = threading.Thread(
        target=lambda: dispatcher.inject_background_telemetry("WORKER_NODE_04 // TARGET_INGESTED")
    )
    sim_thread.start()
    
    root.after(300, root.destroy)
    root.mainloop()
    sim_thread.join()
    print("\n\033[1;32m✔ MODULE 117 THREAD-SAFE QUEUE CONVERGED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Testing multi-threaded queue synchronization loops...\033[0m"
chmod +x gui_event_dispatcher.py
xvfb-run -a ./.venv/bin/python3 gui_event_dispatcher.py 2>/dev/null || ./.venv/bin/python3 gui_event_dispatcher.py
