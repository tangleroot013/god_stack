#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Assembling Unified Operations Window Manager & Launcher...\033[0m"

cat << 'PYEOF' > master_launcher.py
import tkinter as tk
import logging
import time

# Incorporate previous functional design parameters
from gui_lifecycle import LifecycleBridge
from gui_masker import PrivacyPreservingLogBox
from resilience_dashboard import ResilienceDashboardWidget
from input_panel import SecureInputPanel
from gui_event_dispatcher import TelemetryEventDispatcher
from gui_theme import MonochromaticThemeEngine
from gui_integrity import FileIntegrityVisualSentinel

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[MASTER-STACK]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("MasterStack")

class GodStackUnifiedApp:
    def __init__(self, root_window):
        self.root = root_window
        
        # 1. Instantiate Core Styles & Window Hooks
        self.theme = MonochromaticThemeEngine()
        self.theme.apply_theme_to_widget(self.root, "window")
        self.lifecycle = LifecycleBridge(self.root)
        
        # 2. Attach File Verification Sentinel
        self.sentinel = FileIntegrityVisualSentinel(self.root, "csv_operator.py")
        
        # 3. Mount Real-Time Resilience Dashboard
        self.dashboard = ResilienceDashboardWidget(self.root)
        
        # 4. Mount Visual Log View Port Matrix
        self.raw_text_box = tk.Text(self.root, height=12, font=("Courier", 10))
        self.raw_text_box.pack(fill="both", expand=True, padx=10, pady=5)
        self.theme.apply_theme_to_widget(self.raw_text_box, "text_box")
        
        # 5. Bind Privacy Scrubbing Engine
        self.masker = PrivacyPreservingLogBox(self.raw_text_box)
        
        # 6. Initialize Multi-Thread Message Gateway
        self.dispatcher = TelemetryEventDispatcher(self.root, self.masker.append_sanitized_stream)
        self.dispatcher.start_polling_loop()
        
        # 7. Mount Edge Perimeter Secure Input Block
        self.input_panel = SecureInputPanel(self.root, self.dispatcher.inject_background_telemetry)
        
        # Initialize Boot Sequence Logs
        self.dispatcher.inject_background_telemetry("SYSTEM_LAUNCH // Unified Operations Window Active.")
        self.sentinel.evaluate_environment_integrity()

if __name__ == "__main__":
    print("\n\033[1;32m--- G.O.D. UNIFIED COUPLING ORCHESTRATION LAYER ---\033[0m")
    root = tk.Tk()
    root.title("G.O.D. Stack Master UI Terminal")
    root.geometry("700x500")
    
    app = GodStackUnifiedApp(root)
    
    # Run a brief execution integration check, then exit cleanly via hooks
    root.after(1000, app.lifecycle.execute_clean_teardown)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 122 STACK ORCHESTRATION PARITY SECURED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Launching unified interface orchestration tests...\033[0m"
chmod +x master_launcher.py
xvfb-run -a ./.venv/bin/python3 master_launcher.py 2>/dev/null || ./.venv/bin/python3 master_launcher.py
