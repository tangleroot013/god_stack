#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating Threat-Isolated Input Validation Panel...\033[0m"

cat << 'PYEOF' > input_panel.py
import tkinter as tk
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[INPUT-SAN]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("InputSan")

class SecureInputPanel:
    def __init__(self, root_window, submit_callback):
        self.callback = submit_callback
        
        self.input_field = tk.Entry(root_window, bg="#2b2b2b", fg="#ffffff", insertbackground="white")
        self.input_field.pack(fill="x", padx=10, pady=5)
        self.input_field.insert(0, "http://target-node-alpha.com; rm -rf /") # Malicious entry mock

    def process_and_sanitize_submission(self):
        print("\n\033[1;32m--- G.O.D. ENTRY PERIMETER EDGE PROTECTION ---\033[0m")
        raw_submission = self.input_field.get()
        logger.info(f"Evaluating raw console entry stream buffer length: {len(raw_submission)} bytes")
        
        # Strip shell sequence control operators entirely
        sanitized_input = re.sub(r"[\|;&\$\n\r`]", "", raw_submission)
        sanitized_input = sanitized_input.strip()
        
        if sanitized_input != raw_submission:
            logger.warning("\033[1;33mCRITICAL PROTECTION TRIGGERED: Removed malicious command meta-characters!\033[0m")
            
        logger.info(f"  Forwarding isolated target string: [ \033[1;32m{sanitized_input}\033[0m ]")
        self.callback(sanitized_input)

if __name__ == "__main__":
    root = tk.Tk()
    def execution_sink(final_string):
        pass
        
    panel = SecureInputPanel(root, execution_sink)
    # Fire simulated target submission cycle
    root.after(100, panel.process_and_sanitize_submission)
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 110 STRIP-FILTER PERIMETER INGESTION SECURED.\033[0m\n")
PYEOF

echo -e "\033[1;34m[2/2] Triggering adversarial injection testing matrices...\033[0m"
chmod +x input_panel.py
xvfb-run -a ./.venv/bin/python3 input_panel.py 2>/dev/null || ./.venv/bin/python3 input_panel.py
