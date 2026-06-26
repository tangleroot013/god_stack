# ==============================================================================
# G.O.D. STACK TKINTER REALTIME INTELLIGENCE DASHBOARD (ui/god_gui.py)
# Architecture: Multi-Target Input Handler, FOSS Purge, & Extended Operations Matrix
# ==============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import subprocess
import os
import sys
import re

class GodGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("G.O.D. Stack Academic Research Matrix Hub")
        self.root.geometry("1050x700") # Expanded height for extended controls
        self.root.configure(bg="#0F0F12")
        
        self.msg_queue = queue.Queue()
        self.ansi_cleaner = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        
        self.setup_styles()
        self.build_ui()
        self.configure_tags()
        
        # Continuous non-blocking log ingestion loop
        self.root.after(50, self.process_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#0F0F12", foreground="#FFFFFF")
        style.configure("TButton", background="#1A1A24", foreground="#00FF66", 
                        font=("Courier", 10, "bold"), borderwidth=1, focuscolor="none")
        style.map("TButton", background=[("active", "#2A2A3A")])
        style.configure("TLabel", background="#0F0F12", foreground="#8A8A93", font=("Courier", 10))

    def build_ui(self):
        # Header Status Ribbon
        header = tk.Frame(self.root, bg="#16161F", height=45)
        header.pack(fill=tk.X, side=tk.TOP)
        
        title_lbl = tk.Label(header, text="🟢 G.O.D. STACK CORE MATRIX // COGNITIVE RESEARCH PIPELINE", 
                             font=("Courier", 12, "bold"), fg="#00FF66", bg="#16161F")
        title_lbl.pack(pady=10, padx=20, side=tk.LEFT)

        # Main Split Frame Workspace
        workspace = tk.Frame(self.root, bg="#0F0F12")
        workspace.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left Column: Ingestion & Control Hub
        left_panel = tk.Frame(workspace, bg="#0F0F12", width=340)
        left_panel.pack(fill=tk.Y, side=tk.LEFT, padx=(0, 10))
        left_panel.pack_propagate(False)

        input_lbl = ttk.Label(left_panel, text="Academic Target Ingestion Matrix:\n(Paste one website URL per line)")
        input_lbl.pack(anchor=tk.W, pady=(0, 5))

        # Multi-line Site Input Box
        self.target_input = scrolledtext.ScrolledText(left_panel, bg="#16161F", fg="#FFFFFF",
                                                      insertbackground="#FFFFFF", font=("Courier", 10),
                                                      wrap=tk.WORD, bd=1, highlightthickness=1,
                                                      highlightcolor="#3A3A4A", highlightbackground="#1A1A24")
        self.target_input.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Populate Default Seeds for Academic Testing
        self.target_input.insert(tk.END, "HTTPS://NEWS.YCOMBINATOR.COM/newest/?utm_source=rss\n//news.ycombinator.com/front?id=999#comments\n")

        # Action Execution Grid
        run_btn = ttk.Button(left_panel, text="⚡ Launch Research Pipeline", command=self.trigger_pipeline)
        run_btn.pack(fill=tk.X, pady=3)

        mutate_btn = ttk.Button(left_panel, text="🧬 Rotate Stealth Heuristics", command=self.trigger_mutation)
        mutate_btn.pack(fill=tk.X, pady=3)

        alchemist_btn = ttk.Button(left_panel, text="⚗️ Transmute Logs to CSV", command=self.trigger_transmutation)
        alchemist_btn.pack(fill=tk.X, pady=3)

        audit_btn = ttk.Button(left_panel, text="🔍 Check Log Integrity", command=self.trigger_audit)
        audit_btn.pack(fill=tk.X, pady=3)

        clear_btn = ttk.Button(left_panel, text="🧹 Clear UI Console Display", command=self.clear_console)
        clear_btn.pack(fill=tk.X, pady=3)

        purge_btn = ttk.Button(left_panel, text="❌ Secure Log Footprint Purge", command=self.trigger_footprint_purge)
        purge_btn.pack(fill=tk.X, pady=3)

        # Right Column: Output Human Friendly Logs
        right_panel = tk.Frame(workspace, bg="#0F0F12")
        right_panel.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        output_lbl = ttk.Label(right_panel, text="Realtime Audited Stream Telemetry:")
        output_lbl.pack(anchor=tk.W, pady=(0, 5))

        self.console = scrolledtext.ScrolledText(right_panel, bg="#0A0A0D", fg="#D2D2D9",
                                                 insertbackground="#FFFFFF", font=("Courier", 10),
                                                 wrap=tk.WORD, bd=0, highlightthickness=0)
        self.console.pack(fill=tk.BOTH, expand=True)
        self.append_human_log("[SYSTEM-INIT] Dashboard interface bound online. Core units unified.\n")

    def configure_tags(self):
        self.console.tag_config("SUCCESS", foreground="#00FF66", font=("Courier", 10, "bold"))
        self.console.tag_config("PASSED", foreground="#00FF66", font=("Courier", 10, "bold"))
        self.console.tag_config("ERROR", foreground="#FF3366", font=("Courier", 10, "bold"))
        self.console.tag_config("WARNING", foreground="#FFCC00")
        self.console.tag_config("ALERT", foreground="#FF9900", font=("Courier", 10, "italic"))
        self.console.tag_config("INFO", foreground="#33CCFF")
        self.console.tag_config("SYSTEM", foreground="#BD93F9", font=("Courier", 10, "bold"))

    def append_human_log(self, raw_line):
        clean_line = self.ansi_cleaner.sub('', raw_line)
        start_index = self.console.index(tk.END + "-1c")
        self.console.insert(tk.END, clean_line)
        end_index = self.console.index(tk.END)
        
        if "[SUCCESS]" in clean_line or "[PERFECT]" in clean_line:
            self.console.tag_add("SUCCESS", start_index, end_index)
        elif "[PASSED]" in clean_line:
            self.console.tag_add("PASSED", start_index, end_index)
        elif "[ERROR]" in clean_line or "[CRITICAL]" in clean_line or "❌" in clean_line:
            self.console.tag_add("ERROR", start_index, end_index)
        elif "⚠️" in clean_line or "Perimeter Alert" in clean_line:
            self.console.tag_add("ALERT", start_index, end_index)
        elif "[WARNING]" in clean_line or "[NOTICE]" in clean_line:
            self.console.tag_add("WARNING", start_index, end_index)
        elif "[GUI-INFO]" in clean_line or "[ENGINE-CRON]" in clean_line or "[SYSTEM-ACTION]" in clean_line or "[STEALTH-MUTATOR]" in clean_line or "[ALCHEMIST]" in clean_line:
            self.console.tag_add("INFO", start_index, end_index)
        elif "[SYSTEM" in clean_line or "STEP:" in clean_line:
            self.console.tag_add("SYSTEM", start_index, end_index)
            
        self.console.see(tk.END)

    def clear_console(self):
        self.console.delete('1.0', tk.END)
        self.append_human_log("[SYSTEM-ACTION] Local GUI view window console truncated.\n")

    def trigger_mutation(self):
        self.append_human_log("[SYSTEM-ACTION] Launching async runtime fingerprint mutation...\n")
        threading.Thread(target=self.execute_subprocess_worker, args=(".venv/bin/python3 stealth_mutator.py",), daemon=True).start()

    def trigger_transmutation(self):
        self.append_human_log("[SYSTEM-ACTION] Initializing raw payload relational dataset compilation...\n")
        threading.Thread(target=self.execute_subprocess_worker, args=(".venv/bin/python3 data_alchemist.py",), daemon=True).start()

    def trigger_footprint_purge(self):
        confirm = messagebox.askyesno(
            title="Confirm FOSS Footprint Purge Request",
            message="CRITICAL DATA DELETION ALERT:\n\nThis will permanently delete all physical runtime verification logs and tracking artifacts from disk storage namespaces.\n\nAre you sure you want to proceed?",
            icon="warning"
        )
        if confirm:
            self.append_human_log("[SYSTEM-ACTION] Confirmation validation accepted. Running asynchronous storage scrub...\n")
            threading.Thread(target=self.execute_subprocess_worker, args=("./verify_logs.sh --purge",), daemon=True).start()
        else:
            self.append_human_log("[SYSTEM-INFO] Footprint purge aborted by user request.\n")

    def process_queue(self):
        while not self.msg_queue.empty():
            try:
                msg_type, msg_val = self.msg_queue.get_nowait()
                if msg_type == "LOG":
                    self.append_human_log(msg_val)
            except queue.Empty:
                break
        self.root.after(50, self.process_queue)

    def execute_subprocess_worker(self, cmd):
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in iter(process.stdout.readline, ''):
                self.msg_queue.put(("LOG", line))
            process.stdout.close()
            process.wait()
            self.msg_queue.put(("LOG", f"[SYSTEM-INFO] Process context completed with exit code: {process.returncode}\n"))
        except Exception as exc:
            self.msg_queue.put(("LOG", f"[ERROR] Subprocess routine crashed unexpectedly: {exc}\n"))

    def trigger_pipeline(self):
        raw_text = self.target_input.get("1.0", tk.END).strip()
        urls = [line.strip() for line in raw_text.split("\n") if line.strip()]
        if not urls:
            self.append_human_log("[WARNING] Targets omitted. Input research fields must be populated.\n")
            return
        self.append_human_log(f"[SYSTEM-INFO] Injecting {len(urls)} research vectors into the active grid pipeline...\n")
        threading.Thread(target=self.execute_subprocess_worker, args=(".venv/bin/python3 run_stack_pipeline.py",), daemon=True).start()

    def trigger_audit(self):
        self.append_human_log("[SYSTEM-INFO] Initializing system log file security audit...\n")
        threading.Thread(target=self.execute_subprocess_worker, args=("./verify_logs.sh",), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = GodGuiApp(root)
    root.mainloop()
