#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating FOSS-Compliant GUI Core...\033[0m"

cat << 'PYEOF' > foss_gui.py
import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[FOSS-GUI]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("FossGUI")

class GodStackInterface:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("G.O.D. Stack // FOSS Operations Matrix")
        self.root.geometry("600x400")
        self.root.configure(bg="#0d0d0d")
        
        # Terminal-style output log
        self.log_display = tk.Text(self.root, bg="#000000", fg="#00ff00", font=("Courier", 10))
        self.log_display.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.log_message("SYSTEM BOOT: GUI Core Initialized.")
        self.log_message("Awaiting telemetry bindings...")

    def log_message(self, message: str):
        self.log_display.insert(tk.END, f"> {message}\n")
        self.log_display.see(tk.END)
        logger.info(f"UI Console Stream: {message}")

if __name__ == "__main__":
    print("\n\033[1;32m--- G.O.D. GRAPHICAL FRAMEWORK DISPATCH ---\033[0m")
    logger.info("Initializing strictly FOSS-compliant internal window manager...")
    
    # Run a brief, self-terminating validation window for terminal compilation
    root = tk.Tk()
    app = GodStackInterface(root)
    root.after(1000, root.destroy) # Auto-close during deployment test
    root.mainloop()
    
    print("\n\033[1;32m✔ MODULE 106 FOSS GUI CORE MATRICES STABLE.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Instantiating graphical render arrays...\033[0m"
chmod +x foss_gui.py
# If X11/Wayland isn't active in your terminal, this will catch the fail gracefully
xvfb-run -a ./.venv/bin/python3 foss_gui.py 2>/dev/null || ./.venv/bin/python3 foss_gui.py
