#!/usr/bin/env python3
# =============================================================================
# G.O.D. STACK v2.0 POWER-USER TUI/GUI TERMINAL
# Architecture: FOSS Centric, Asynchronous Subprocess Execution, Non-Blocking
# =============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import sys
import os

class PowerUserConsole:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 G.O.D. STACK v2.0 // CONTROL MATRIX")
        self.root.geometry("1000x650")
        self.root.configure(bg="#050505")

        # Legacy Matrix Terminal Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(".", background="#050505", foreground="#00FF00")
        self.style.configure("TLabel", background="#050505", foreground="#00FF00", font=("Courier", 11, "bold"))
        self.style.configure("TButton", background="#111111", foreground="#00FF00", font=("Courier", 10, "bold"), borderwidth=1)
        self.style.map("TButton", background=[("active", "#00FF00")], foreground=[("active", "#000000")])

        # Core Header
        header = ttk.Label(self.root, text="=== G.O.D. STACK VERSION 2.0.0 // HARDENED OPERATOR SYSTEM ===", anchor="center")
        header.pack(fill=tk.X, pady=10)

        # Split Windows
        main_frame = tk.Frame(self.root, bg="#050505")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Control Panel Left
        control_panel = tk.LabelFrame(main_frame, text=" SYSTEM INJECTIONS ", bg="#050505", fg="#00FF00", font=("Courier", 10, "bold"))
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Scripts Mapping
        self.target_scripts = [
            ("1. Sync & Verify Logs", "verify_logs.sh"),
            ("2. Harvest Egress Proxies", "scavenger.py"),
            ("3. Fire Unified GodEngine", "god_engine.py"),
            ("4. Playwright Stealth Matrix", "god_scraper.py"),
            ("5. Local Stack Heartbeat", "daemon_core.py"),
            ("6. Deploy Production Patch", "finalize_deployment.sh"),
            ("7. Run Status Matrix", "prod_status.sh")
        ]

        for text, script in self.target_scripts:
            btn = ttk.Button(control_panel, text=text, command=lambda s=script: self.dispatch_thread(s))
            btn.pack(fill=tk.X, padx=10, pady=6)

        # System Logging Window (Right)
        log_panel = tk.LabelFrame(main_frame, text=" REAL-TIME SUBPROCESS OUTPUT STREAMS ", bg="#050505", fg="#00FF00", font=("Courier", 10, "bold"))
        log_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.console_out = scrolledtext.ScrolledText(
            log_panel, bg="#000000", fg="#00FF00", insertbackground="#00FF00",
            font=("Courier", 10), state=tk.DISABLED
        )
        self.console_out.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status Bar Footer
        self.status_var = tk.StringVar(value="SYSTEM: STANDBY [AWAITING USER INJECTION]")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg="#111111", fg="#00FF00", font=("Courier", 9), anchor="w")
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=3)

    def write_to_console(self, text):
        self.console_out.configure(state=tk.NORMAL)
        self.console_out.insert(tk.END, text)
        self.console_out.see(tk.END)
        self.console_out.configure(state=tk.DISABLED)

    def dispatch_thread(self, script_name):
        thread = threading.Thread(target=self.execute_script, args=(script_name,), daemon=True)
        thread.start()

    def execute_script(self, script_name):
        self.status_var.set(f"EXECUTING: {script_name}...")
        self.write_to_console(f"\n>>> Initializing subprocess pipeline context: {script_name}\n")
        
        # Navigate relative up to core project directory if needed
        cmd = ["python3", script_name] if script_name.endswith(".py") else ["bash", script_name]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                self.write_to_console(line)
                
            process.wait()
            if process.returncode == 0:
                self.status_var.set(f"SUCCESS: {script_name} finished without fault.")
            else:
                self.status_var.set(f"ANOMALY: {script_name} dropped execution code {process.returncode}")
        except Exception as e:
            self.write_to_console(f"[ERROR EXCEPTION]: Failed to hook or locate workspace module. {str(e)}\n")
            self.status_var.set("SYSTEM: RUNTIME FAULT")

if __name__ == "__main__":
    root = tk.Tk()
    app = PowerUserConsole(root)
    root.mainloop()
