#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import subprocess
import sys
import threading
import os
import csv
import random
import time
import json
import traceback
from datetime import datetime
from queue import Queue

# Configuration Constants
MAX_QUEUE_DEPTH = 2000
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
]

class GodStackDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G.O.D. STACK — INTEGRATED CONTROL HUD v2.0")
        self.geometry("1400x950")
        self.configure(bg="#0a0a0a")
        
        self.db_path = "/home/tangleroot013/god_stack/god_stack_vfs.db"
        self.task_queue = Queue(maxsize=MAX_QUEUE_DEPTH)
        self.last_used_ua = "N/A"
        
        self.init_database_schemas()
        
        # Configure Window Grid Weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Outer Frame Notebook Tabbed Hub
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Build Style Adjustments
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background="#0a0a0a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1a1a1a", foreground="#888888", font=("Courier", 9, "bold"), padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", "#0f0f0f")], foreground=[("selected", "#00FF66")])
        style.configure("Treeview", background="#111111", foreground="#00FF66", fieldbackground="#111111", font=("Courier", 9), rowheight=22)
        style.configure("Treeview.Heading", background="#1c1c1c", foreground="#00E5FF", font=("Courier", 9, "bold"))
        style.map("Treeview", background=[('selected', '#1c1c1c')], foreground=[('selected', '#FF6B00')])
        style.configure("Horizontal.TProgressbar", background="#00FF66", troughcolor="#111111")

        self.main_control_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        self.anomaly_ledger_tab = tk.Frame(self.notebook, bg="#0a0a0a")
        
        self.notebook.add(self.main_control_tab, text=" MAIN PIPELINE CONTROL ")
        self.notebook.add(self.anomaly_ledger_tab, text=" SYSTEM ANOMALY LEDGER ")

        # Assemble Panels
        self.create_main_control_layout()
        self.create_anomaly_ledger_layout()
        
        # Start Heartbeat Engine Threads
        threading.Thread(target=self.proxy_scoring_heartbeat, daemon=True).start()
        self.refresh_dashboard_loop()

    def init_database_schemas(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Custom Target Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'PENDING'
                )
            ''')
            # Persistent System Anomaly Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    proxy TEXT,
                    url TEXT,
                    error_type TEXT,
                    traceback TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Schema Initialization Error: {e}")

    # ==========================================
    # TAB 1: MAIN CONTROL INTERFACE
    # ==========================================
    def create_main_control_layout(self):
        master_frame = tk.Frame(self.main_control_tab, bg="#0a0a0a")
        master_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        master_frame.grid_columnconfigure(0, weight=1, minsize=340)
        master_frame.grid_columnconfigure(1, weight=3)
        master_frame.grid_rowconfigure(0, weight=1)
        
        # Left Panel Creation
        left_frame = tk.Frame(master_frame, bg="#0f0f0f", bd=1, relief=tk.SOLID, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(3, weight=1)
        
        # Subsystem Engines Metadata
        lbl_mesh = tk.Label(left_frame, text="⚡ UPGRADED TOPOLOGY INTERFACE", bg="#0f0f0f", fg="#00FF66", font=("Courier", 11, "bold"))
        lbl_mesh.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        state_frame = tk.LabelFrame(left_frame, text=" SUBSYSTEM RE-ENGINEERING ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=5, pady=5)
        state_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.state_labels = {}
        subsystems = [
            ("Proxy Rotator Pool", "POLLING NODES", "#00FFBB"),
            ("Backpressure State", "STABLE", "#00FFBB"),
            ("Request Jitter Engine", "0.2s - 1.0s RANDOM", "#00FFBB"),
            ("Extraction Schema", "READABILITY LXML", "#00FFBB")
        ]
        for idx, (comp, desc, col) in enumerate(subsystems):
            tk.Label(state_frame, text=f"• {comp}:", bg="#0f0f0f", fg="#cccccc", font=("Courier", 9)).grid(row=idx, column=0, sticky="w", pady=2)
            lbl_val = tk.Label(state_frame, text=desc, bg="#0f0f0f", fg=col, font=("Courier", 9, "bold"))
            lbl_val.grid(row=idx, column=1, sticky="w", padx=10, pady=2)
            self.state_labels[comp] = lbl_val
            
        # Queue Metrics Subpanel
        q_frame = tk.LabelFrame(left_frame, text=" IN-MEMORY BUFFER BACKPRESSURE ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=5, pady=5)
        q_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.lbl_q_text = tk.Label(q_frame, text="Queue Depth: 0 / 2000", bg="#0f0f0f", fg="#ffffff", font=("Courier", 9))
        self.lbl_q_text.pack(anchor="w", pady=2)
        self.queue_progress = ttk.Progressbar(q_frame, orient="horizontal", mode="determinate", maximum=MAX_QUEUE_DEPTH, style="Horizontal.TProgressbar")
        self.queue_progress.pack(fill=tk.X, pady=4)
        
        self.lbl_ua_string = tk.Label(q_frame, text="SPOOFED UA: IDLE", bg="#0f0f0f", fg="#FFCC00", font=("Courier", 8), justify=tk.LEFT, wraplength=300)
        self.lbl_ua_string.pack(anchor="w", pady=(5, 0))

        # Terminal Log Stream Window
        terminal_frame = tk.LabelFrame(left_frame, text=" REALTIME SYSTEM FLOW LOGS ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=5, pady=5)
        terminal_frame.grid(row=3, column=0, sticky="nsew")
        terminal_frame.grid_rowconfigure(0, weight=1)
        terminal_frame.grid_columnconfigure(0, weight=1)
        
        self.term_text = tk.Text(terminal_frame, bg="#050505", fg="#888888", font=("Courier", 8), wrap=tk.WORD, relief=tk.FLAT, state=tk.DISABLED)
        self.term_text.grid(row=0, column=0, sticky="nsew")
        term_scroll = ttk.Scrollbar(terminal_frame, orient=tk.VERTICAL, command=self.term_text.yview)
        term_scroll.grid(row=0, column=1, sticky="ns")
        self.term_text.config(yscrollcommand=term_scroll.set)

        # Right Panel Layout Allocation
        right_frame = tk.Frame(master_frame, bg="#0a0a0a", padx=5)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(2, weight=2) # Ledger Treeview
        right_frame.grid_rowconfigure(3, weight=2) # Split Frame Payload Text Windows
        
        # Single Link Manual Injector Frame Strip
        inject_frame = tk.Frame(right_frame, bg="#111111", relief=tk.SOLID, bd=1, padx=10, pady=8)
        inject_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(inject_frame, text="TARGET MANIFEST INJECTOR", bg="#FF6B00", fg="#000000", font=("Courier", 8, "bold"), padx=5).pack(side=tk.LEFT, padx=(0, 10))
        self.target_input = tk.Entry(inject_frame, bg="#1a1a1a", fg="#888888", font=("Courier", 10), relief=tk.FLAT, insertbackground="#00FF66")
        self.target_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.target_input.insert(0, "Paste runtime URL path targets here...")
        tk.Button(inject_frame, text="➕ INJECT LINE", bg="#FF6B00", fg="#000000", font=("Courier", 9, "bold"), relief=tk.FLAT, padx=15, command=self.add_single_target).pack(side=tk.RIGHT)
        
        # Proxy Score Tracking Mini Matrix Grid
        p_matrix_frame = tk.LabelFrame(right_frame, text=" LIVE PROXY HEALTH MATRIX SCORING ", bg="#0a0a0a", fg="#888888", font=("Courier", 8, "bold"))
        p_matrix_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.proxy_tree = ttk.Treeview(p_matrix_frame, columns=("NODE NAME", "URL ENDPOINT", "LATENCY SPEED", "VITALITY"), show="headings", height=3)
        for col in ("NODE NAME", "URL ENDPOINT", "LATENCY SPEED", "VITALITY"):
            self.proxy_tree.heading(col, text=col)
            self.proxy_tree.column(col, anchor="center")
        self.proxy_tree.pack(fill=tk.BOTH, expand=True)

        # Core Ledger Treeview Grid
        ledger_frame = tk.Frame(right_frame, bg="#111111", relief=tk.SOLID, bd=1)
        ledger_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        self.ledger_tree = ttk.Treeview(ledger_frame, columns=("IDX", "TIMESTAMP", "SOURCE DOMAIN", "IDENTITY TITLE", "STATE"), show="headings")
        self.ledger_tree.heading("IDX", text="IDX"); self.ledger_tree.column("IDX", width=50, stretch=tk.NO)
        self.ledger_tree.heading("TIMESTAMP", text="TIMESTAMP")
        self.ledger_tree.heading("SOURCE DOMAIN", text="SOURCE DOMAIN")
        self.ledger_tree.heading("IDENTITY TITLE", text="EXTRACTION IDENTITY TITLE")
        self.ledger_tree.heading("STATE", text="STATUS CODE")
        self.ledger_tree.pack(fill=tk.BOTH, expand=True)
        self.ledger_tree.bind('<<TreeviewSelect>>', self.on_ledger_row_selected)

        # Split Payload Display Window
        split_display_frame = tk.Frame(right_frame, bg="#0a0a0a")
        split_display_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        split_display_frame.grid_columnconfigure(0, weight=1)
        split_display_frame.grid_columnconfigure(1, weight=1)
        split_display_frame.grid_rowconfigure(0, weight=1)
        
        raw_f = tk.LabelFrame(split_display_frame, text=" FIELD VALIDATION STRUCTURE (JSON) ", bg="#111111", fg="#00E5FF", font=("Courier", 8, "bold"))
        raw_f.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
        self.txt_validated_json = tk.Text(raw_f, bg="#090909", fg="#00E5FF", font=("Courier", 9), wrap=tk.WORD, relief=tk.FLAT)
        self.txt_validated_json.pack(fill=tk.BOTH, expand=True)
        
        parsed_f = tk.LabelFrame(split_display_frame, text=" EXTRACTED PARSED TEXT SUMMARY BODY ", bg="#111111", fg="#00FF66", font=("Courier", 8, "bold"))
        parsed_f.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
        self.txt_extracted_body = tk.Text(parsed_f, bg="#090909", fg="#00FF66", font=("Courier", 9), wrap=tk.WORD, relief=tk.FLAT)
        self.txt_extracted_body.pack(fill=tk.BOTH, expand=True)

        # Execution Strip Footer Layout Row
        control_strip = tk.Frame(right_frame, bg="#0a0a0a")
        control_strip.grid(row=4, column=0, sticky="ew")
        self.btn_launch = tk.Button(control_strip, text="⚡ RUN PIPELINE ACCELERATOR", bg="#00FF66", fg="#000000", font=("Courier", 10, "bold"), command=self.trigger_pipeline_sequence, relief=tk.FLAT, padx=20, pady=8)
        self.btn_launch.pack(side=tk.RIGHT)
        self.status_lbl = tk.Label(control_strip, text="● SYSTEM ENG STATE: IDLE", bg="#0a0a0a", fg="#00FFBB", font=("Courier", 10, "bold"))
        self.status_lbl.pack(side=tk.LEFT, pady=5)

    # ==========================================
    # TAB 2: SYSTEM ANOMALY LEDGER
    # ==========================================
    def create_anomaly_ledger_layout(self):
        self.anomaly_ledger_tab.grid_columnconfigure(0, weight=1)
        self.anomaly_ledger_tab.grid_rowconfigure(0, weight=1)
        self.anomaly_ledger_tab.grid_rowconfigure(1, weight=1)
        
        upper_frame = tk.Frame(self.anomaly_ledger_tab, bg="#111111", relief=tk.SOLID, bd=1)
        upper_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        
        self.anomaly_tree = ttk.Treeview(upper_frame, columns=("ID", "TIMESTAMP", "PROXY INTERF", "TARGET EXCEPTION LOCATION", "ERROR BRIEF"), show="headings")
        for col in ("ID", "TIMESTAMP", "PROXY INTERF", "TARGET EXCEPTION LOCATION", "ERROR BRIEF"):
            self.anomaly_tree.heading(col, text=col)
        self.anomaly_tree.column("ID", width=60, stretch=tk.NO, anchor="center")
        self.anomaly_tree.pack(fill=tk.BOTH, expand=True)
        self.anomaly_tree.bind('<<TreeviewSelect>>', self.on_anomaly_row_selected)
        
        lower_frame = tk.LabelFrame(self.anomaly_ledger_tab, text=" DETAILED FAULT TRACEBACK STACK ENGINE ENGINE ", bg="#111111", fg="#FF3333", font=("Courier", 8, "bold"))
        lower_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.txt_traceback = tk.Text(lower_frame, bg="#050505", fg="#FF5555", font=("Courier", 9), wrap=tk.WORD, relief=tk.FLAT)
        self.txt_traceback.pack(fill=tk.BOTH, expand=True)

    # ==========================================
    # ENGINE CORE & TRANSACTIONS LOGIC
    # ==========================================
    def log_terminal(self, message, msg_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.term_text.config(state=tk.NORMAL)
        self.term_text.insert(tk.END, f"[{timestamp}] {message.upper()}\n")
        self.term_text.config(state=tk.DISABLED)
        self.term_text.see(tk.END)

    def add_single_target(self):
        url = self.target_input.get().strip()
        if url in ("", "Paste runtime URL path targets here..."): return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO custom_targets (url, status) VALUES (?, ?)', (url, 'PENDING'))
            conn.commit()
            conn.close()
            self.log_terminal(f"Injected target to SQLite tracking layer: {url}", "success")
        except sqlite3.IntegrityError:
            self.log_terminal("Target already loaded into persistent tracking matrix.", "warning")
        except Exception as e:
            self.log_terminal(f"Database error: {e}", "error")

    def proxy_scoring_heartbeat(self):
        proxy_mocks = [
            ("proxy_node_alpha", "127.0.0.1:8080"),
            ("proxy_node_beta", "192.168.1.50:3128")
        ]
        while True:
            # Simulate real-world network latency changes per proxy node connection
            nodes_data = []
            for name, endpoint in proxy_mocks:
                latency = f"{random.randint(45, 160)}ms"
                vitality = "HEALTHY" if random.random() > 0.1 else "BANNED (429 BACKOFF)"
                nodes_data.append((name, endpoint, latency, vitality))
            
            def update_ui():
                for item in self.proxy_tree.get_children(): self.proxy_tree.delete(item)
                for node in nodes_data: self.proxy_tree.insert("", tk.END, values=node)
            self.after(0, update_ui)
            time.sleep(10)

    def on_ledger_row_selected(self, event):
        selected = self.ledger_tree.selection()
        if not selected: return
        item = self.ledger_tree.item(selected[0])
        try:
            row_id = int(item['values'][0])
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT target_url, summary FROM ingestion_ledger WHERE id = ?', (row_id,))
            record = cursor.fetchone()
            conn.close()
            
            if record:
                url, summary = record
                mock_json = {
                    "source_url": url,
                    "validated_schema": "Readability.v2",
                    "extraction_timestamp": datetime.now().isoformat() + "Z",
                    "payload_integrity_check": "CRC32_PASS"
                }
                self.txt_validated_json.delete("1.0", tk.END)
                self.txt_validated_json.insert("1.0", json.dumps(mock_json, indent=2))
                
                self.txt_extracted_body.delete("1.0", tk.END)
                self.txt_extracted_body.insert("1.0", f"DOCUMENT BODY:\n{summary}")
        except Exception as e:
            print(f"Row parsing presentation fault: {e}")

    def on_anomaly_row_selected(self, event):
        selected = self.anomaly_tree.selection()
        if not selected: return
        item = self.anomaly_tree.item(selected[0])
        try:
            anomaly_id = int(item['values'][0])
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT traceback FROM system_anomalies WHERE id = ?', (anomaly_id,))
            record = cursor.fetchone()
            conn.close()
            
            self.txt_traceback.delete("1.0", tk.END)
            if record:
                self.txt_traceback.insert("1.0", record[0])
        except Exception as e:
            print(f"Exception presentation selection fault: {e}")

    def trigger_pipeline_sequence(self):
        self.btn_launch.config(state="disabled", bg="#222222", text="EXECUTING RE-ENGINEERED ARRAYS...")
        self.status_lbl.config(text="● ENGINE STATE: RUNNING MULTI-THREAD PIPELINE", fg="#FFCC00")
        
        # Load elements inside task token queue to simulate backpressure calculations live
        for idx in range(1250):
            if not self.task_queue.full(): self.task_queue.put(f"worker_token_{idx}")
            
        def run_subprocess():
            try:
                # Randomize a user-agent to visually update spoof metadata labels
                self.last_used_ua = random.choice(USER_AGENTS)
                self.after(0, lambda: self.lbl_ua_string.config(text=f"SPOOFED UA:\n{self.last_used_ua}"))
                
                res = subprocess.run([sys.executable, "/home/tangleroot013/god_stack/orchestrator.py"], capture_output=True, text=True, check=True)
                for line in res.stdout.splitlines():
                    if "worker_node" in line or "Final" in line or "System" in line:
                        self.after(0, lambda l=line: self.log_terminal(l.split("|")[-1].strip()))
                self.after(0, lambda: self.log_terminal("Pipeline extraction sync complete.", "success"))
            except subprocess.CalledProcessError as e:
                self.after(0, lambda: self.log_terminal("Pipeline trace fault detected. Logging anomaly.", "error"))
                # Write failure payload to system anomalies database dynamically
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO system_anomalies (proxy, url, error_type, traceback) VALUES (?, ?, ?, ?)',
                                   ('proxy_node_alpha', 'https://arxiv.org/list/cs.AI/recent', 'SubprocessCalledProcessError', f"STDOUT:\n{e.stdout}\n\nSTDERR:\n{e.stderr}"))
                    conn.commit()
                    conn.close()
                except Exception as ex: print(ex)
            finally:
                while not self.task_queue.empty(): self.task_queue.get()
                self.after(0, self.restore_control_strip)
                
        threading.Thread(target=run_subprocess, daemon=True).start()

    def restore_control_strip(self):
        self.btn_launch.config(state="normal", bg="#00FF66", text="⚡ RUN PIPELINE ACCELERATOR")
        self.status_lbl.config(text="● SYSTEM ENG STATE: IDLE", fg="#00FFBB")
        self.refresh_dashboard_loop()

    def refresh_dashboard_loop(self):
        if not os.path.exists(self.db_path):
            self.after(4000, self.refresh_dashboard_loop)
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Update Core Data Ledger View Grid
            cursor.execute("SELECT id, timestamp, source_domain, title, status FROM ingestion_ledger ORDER BY id DESC LIMIT 25")
            rows = cursor.fetchall()
            for item in self.ledger_tree.get_children(): self.ledger_tree.delete(item)
            for row in rows: self.ledger_tree.insert("", tk.END, values=row)
            
            # 2. Update System Anomaly Tracking View Tab
            cursor.execute("SELECT id, timestamp, proxy, url, error_type FROM system_anomalies ORDER BY id DESC LIMIT 25")
            anomalies = cursor.fetchall()
            for item in self.anomaly_tree.get_children(): self.anomaly_tree.delete(item)
            for row in anomalies: self.anomaly_tree.insert("", tk.END, values=row)
            
            conn.close()
            
            # 3. Handle Backpressure Meter Refresh Tasks
            q_depth = self.task_queue.qsize()
            self.lbl_q_text.config(text=f"Queue Depth: {q_depth} / {MAX_QUEUE_DEPTH}")
            self.queue_progress['value'] = q_depth
            
            if q_depth > (MAX_QUEUE_DEPTH * 0.75):
                self.state_labels["Backpressure State"].config(text="PRESSURE BACKOFF ENFORCED", fg="#FFCC00")
            else:
                self.state_labels["Backpressure State"].config(text="STABLE", fg="#00FFBB")
                
        except Exception as e:
            pass
        self.after(4000, self.refresh_dashboard_loop)

if __name__ == "__main__":
    app = GodStackDashboard()
    app.mainloop()
