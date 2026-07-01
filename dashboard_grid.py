#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import subprocess
import sys
import threading
import os
import csv
from datetime import datetime

class GodStackDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G.O.D. STACK — INTEGRATED CONTROL HUD")
        self.geometry("1300x900")
        self.configure(bg="#0a0a0a")
        
        self.db_path = "/home/tangleroot013/god_stack/god_stack_vfs.db"
        self.init_custom_targets_table()
        
        # Configure Root Window Expansion
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Outer Wrapper
        self.master_frame = tk.Frame(self, bg="#0a0a0a", padx=10, pady=10)
        self.master_frame.grid(row=0, column=0, sticky="nsew")
        
        # Master Grid Layout Allocation
        # Left Panel (Topology & System States): Width=1
        # Right Panel (Ledger Matrix & Raw Payloads): Width=3
        self.master_frame.grid_columnconfigure(0, weight=1, minsize=320)
        self.master_frame.grid_columnconfigure(1, weight=3)
        self.master_frame.grid_rowconfigure(0, weight=1)
        
        self.create_left_panel()
        self.create_right_panel()
        
        # Start background polling loop for active VFS synchronization
        self.refresh_dashboard()

    def init_custom_targets_table(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'PENDING'
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"VFS Shield Initialization Fault: {e}")

    # ==========================================
    # LEFT PANEL: TOPOLOGY, CONTROLS & DIAGNOSTICS
    # ==========================================
    def create_left_panel(self):
        left_frame = tk.Frame(self.master_frame, bg="#0f0f0f", bd=1, relief=tk.SOLID, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=0) # Module Header
        left_frame.grid_rowconfigure(1, weight=0) # Component Checklist
        left_frame.grid_rowconfigure(2, weight=0) # Control Matrix
        left_frame.grid_rowconfigure(3, weight=1) # Live Diagnostic Stream Terminal
        
        # 1. Module Header Text
        lbl_mesh = tk.Label(left_frame, text="⚡ SYSTEM TOPOLOGY INTERFACE", bg="#0f0f0f", fg="#00FF66", font=("Courier", 11, "bold"))
        lbl_mesh.grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # 2. Stack Component Telemetry States Panel
        state_frame = tk.LabelFrame(left_frame, text=" SUBSYSTEM ENGINES ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=5, pady=5)
        state_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        self.states = {
            "Proxy Rotator": ("ACTIVE [ALPHA/BETA]", "#00FFBB"),
            "Rate Limiter": ("SLIDING WINDOW (10 rps)", "#00FFBB"),
            "Circuit Breaker": ("CLOSED (STABLE)", "#00FFBB"),
            "Adaptive Scaler": ("THREADPOOL AUTO", "#00FFBB"),
            "SQLite VFS Layer": ("SYNCHRONIZED", "#00FFBB")
        }
        
        self.state_labels = {}
        for idx, (component, (desc, color)) in enumerate(self.states.items()):
            lbl_comp = tk.Label(state_frame, text=f"• {component}:", bg="#0f0f0f", fg="#cccccc", font=("Courier", 9))
            lbl_comp.grid(row=idx, column=0, sticky="w", pady=2)
            lbl_val = tk.Label(state_frame, text=desc, bg="#0f0f0f", fg=color, font=("Courier", 9, "bold"))
            lbl_val.grid(row=idx, column=1, sticky="w", padx=10, pady=2)
            self.state_labels[component] = lbl_val

        # 3. Queue Execution Actions Frame
        act_frame = tk.LabelFrame(left_frame, text=" MASS LINK INJECTOR & ACTIONS ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=8, pady=8)
        act_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        self.btn_import = tk.Button(act_frame, text="📤 IMPORT TARGETS CSV", bg="#1a1a1a", fg="#00FF66", font=("Courier", 9, "bold"), relief=tk.FLAT, pady=5, command=self.import_csv)
        self.btn_import.pack(fill=tk.X, pady=2)
        
        self.btn_export = tk.Button(act_frame, text="📥 EXPORT DATA LOG CSV", bg="#1a1a1a", fg="#00E5FF", font=("Courier", 9, "bold"), relief=tk.FLAT, pady=5, command=self.export_csv)
        self.btn_export.pack(fill=tk.X, pady=2)
        
        self.btn_clear = tk.Button(act_frame, text="❌ PURGE PENDING QUEUE", bg="#261212", fg="#FF3333", font=("Courier", 9, "bold"), relief=tk.FLAT, pady=5, command=self.clear_pending_targets)
        self.btn_clear.pack(fill=tk.X, pady=2)
        
        # 4. Live Diagnostic Terminal Log Window
        terminal_frame = tk.LabelFrame(left_frame, text=" LIVE TELEMETRY TRANSMISSION DIAGNOSTICS ", bg="#0f0f0f", fg="#888888", font=("Courier", 8, "bold"), padx=5, pady=5)
        terminal_frame.grid(row=3, column=0, sticky="nsew")
        terminal_frame.grid_rowconfigure(0, weight=1)
        terminal_frame.grid_columnconfigure(0, weight=1)
        
        self.term_text = tk.Text(terminal_frame, bg="#050505", fg="#888888", font=("Courier", 8), wrap=tk.WORD, relief=tk.FLAT, state=tk.DISABLED)
        self.term_text.grid(row=0, column=0, sticky="nsew")
        
        term_scroll = ttk.Scrollbar(terminal_frame, orient=tk.VERTICAL, command=self.term_text.yview)
        term_scroll.grid(row=0, column=1, sticky="ns")
        self.term_text.config(yscrollcommand=term_scroll.set)
        
        self.log_terminal("System monitoring hub baseline components initialized.")

    def log_terminal(self, message, msg_type="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = f"[{timestamp}] "
        
        colors = {"info": "#888888", "success": "#00FF66", "warning": "#FFCC00", "error": "#FF3333"}
        txt_color = colors.get(msg_type, "#ffffff")
        
        self.term_text.config(state=tk.NORMAL)
        self.term_text.insert(tk.END, prefix + message.upper() + "\n")
        self.term_text.config(state=tk.DISABLED)
        self.term_text.see(tk.END)

    # ==========================================
    # RIGHT PANEL: LOGS, METRICS & LIVE VISUALIZERS
    # ==========================================
    def create_right_panel(self):
        right_frame = tk.Frame(self.master_frame, bg="#0a0a0a", padx=5)
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(0, weight=0) # Single Target Line Injector
        right_frame.grid_rowconfigure(1, weight=0) # Core Metric KPI Cards
        right_frame.grid_rowconfigure(2, weight=3) # Ledger Database Matrix Grid
        right_frame.grid_rowconfigure(3, weight=2) # Raw Document Payload Summary Stream
        right_frame.grid_rowconfigure(4, weight=0) # Execution Control Strip
        
        # 1. Single Target Line Injector Frame
        inject_frame = tk.Frame(right_frame, bg="#111111", relief=tk.SOLID, bd=1, padx=10, pady=8)
        inject_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        lbl_inj_tag = tk.Label(inject_frame, text="MANUAL TARGET INJECTOR", bg="#FF6B00", fg="#000000", font=("Courier", 8, "bold"), padx=5)
        lbl_inj_tag.pack(side=tk.LEFT, padx=(0, 10))
        
        self.target_input = tk.Entry(inject_frame, bg="#1a1a1a", fg="#666666", font=("Courier", 10), relief=tk.FLAT, insertbackground="#00FF66", bd=4)
        self.target_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.target_input.insert(0, "Paste runtime URL path targets here...")
        
        self.target_input.bind("<FocusIn>", lambda e: self.target_input.delete(0, tk.END) if self.target_input.get() == "Paste runtime URL path targets here..." else None)
        self.target_input.bind("<FocusOut>", lambda e: self.target_input.insert(0, "Paste runtime URL path targets here...") if self.target_input.get() == "" else None)
        
        btn_inj_act = tk.Button(inject_frame, text="➕ INJECT TARGET LINK", bg="#FF6B00", fg="#000000", font=("Courier", 9, "bold"), relief=tk.FLAT, padx=15, command=self.add_target)
        btn_inj_act.pack(side=tk.RIGHT)

        # 2. Telemetry Metric KPI Array Row
        kpi_frame = tk.Frame(right_frame, bg="#0a0a0a")
        kpi_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        kpi_frame.grid_columnconfigure(0, weight=1)
        kpi_frame.grid_columnconfigure(1, weight=1)
        kpi_frame.grid_columnconfigure(2, weight=1)
        
        # Attempts Logged
        card1 = tk.Frame(kpi_frame, bg="#111111", relief=tk.SOLID, bd=1, padx=10, pady=6)
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        tk.Label(card1, text="TOTAL NETWORK ATTEMPTS", bg="#00E5FF", fg="#000000", font=("Courier", 8, "bold")).pack(anchor="w")
        self.lbl_attempts = tk.Label(card1, text="0", bg="#111111", fg="#ffffff", font=("Courier", 16, "bold"))
        self.lbl_attempts.pack(anchor="w", pady=(2, 0))
        
        # Success Logs
        card2 = tk.Frame(kpi_frame, bg="#111111", relief=tk.SOLID, bd=1, padx=10, pady=6)
        card2.grid(row=0, column=1, sticky="ew", padx=4)
        tk.Label(card2, text="VERIFIED PAYLOAD SUCCESSES", bg="#00FF66", fg="#000000", font=("Courier", 8, "bold")).pack(anchor="w")
        self.lbl_successes = tk.Label(card2, text="0", bg="#111111", fg="#00FF66", font=("Courier", 16, "bold"))
        self.lbl_successes.pack(anchor="w", pady=(2, 0))
        
        # Performance Accuracy Metrics
        card3 = tk.Frame(kpi_frame, bg="#111111", relief=tk.SOLID, bd=1, padx=10, pady=6)
        card3.grid(row=0, column=2, sticky="ew", padx=(4, 0))
        tk.Label(card3, text="MATRIX ACCURACY RATE", bg="#FFCC00", fg="#000000", font=("Courier", 8, "bold")).pack(anchor="w")
        self.lbl_yield = tk.Label(card3, text="0.0%", bg="#111111", fg="#FFCC00", font=("Courier", 16, "bold"))
        self.lbl_yield.pack(anchor="w", pady=(2, 0))

        # 3. Ledger Database Matrix Treeview Grid
        ledger_frame = tk.Frame(right_frame, bg="#111111", relief=tk.SOLID, bd=1)
        ledger_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(ledger_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ledger_tree = ttk.Treeview(
            ledger_frame,
            columns=("IDX", "TIMESTAMP", "SOURCE DOMAIN", "EXTRACTION TYPE", "CRYPTO STATUS"),
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.ledger_tree.yview)
        
        self.ledger_tree.heading("#0", text="")
        self.ledger_tree.column("#0", width=0, minwidth=0, stretch=tk.NO)
        self.ledger_tree.heading("IDX", text="IDX")
        self.ledger_tree.column("IDX", width=50, anchor="center", stretch=tk.NO)
        self.ledger_tree.heading("TIMESTAMP", text="TIMESTAMP")
        self.ledger_tree.column("TIMESTAMP", width=150, anchor="center")
        self.ledger_tree.heading("SOURCE DOMAIN", text="SOURCE DOMAIN")
        self.ledger_tree.column("SOURCE DOMAIN", width=180, anchor="w")
        self.ledger_tree.heading("EXTRACTION TYPE", text="EXTRACTION DETAILS")
        self.ledger_tree.column("EXTRACTION TYPE", width=250, anchor="w")
        self.ledger_tree.heading("CRYPTO STATUS", text="CRYPTO INTEG")
        self.ledger_tree.column("CRYPTO STATUS", width=150, anchor="center")
        
        self.ledger_tree.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background="#111111", foreground="#00FF66", fieldbackground="#111111", font=("Courier", 9), rowheight=22)
        style.configure("Treeview.Heading", background="#1c1c1c", foreground="#00E5FF", font=("Courier", 9, "bold"))
        style.map("Treeview", background=[('selected', '#1c1c1c')], foreground=[('selected', '#FF6B00')])
        
        self.ledger_tree.bind('<<TreeviewSelect>>', self.on_ledger_select)

        # 4. Raw Document Payload Summary Stream Panel Window
        detail_frame = tk.Frame(right_frame, bg="#111111", relief=tk.SOLID, bd=1)
        detail_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        
        self.detail_text = tk.Text(detail_frame, bg="#090909", fg="#00E5FF", font=("Courier", 9), wrap=tk.WORD, relief=tk.FLAT, padx=10, pady=10)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.insert("1.0", "[VFS Context Monitor Idle] Highlight a specific transaction record from the index ledger matrix above to view extracted secure stream payloads...")
        self.detail_text.config(state=tk.DISABLED)

        # 5. Core Engine Control Action Bar Strip
        control_frame = tk.Frame(right_frame, bg="#0a0a0a")
        control_frame.grid(row=4, column=0, sticky="ew")
        
        self.btn_launch = tk.Button(
            control_frame, text="⚡ EXECUTE PIPELINE MATRIX", bg="#00FF66", fg="#000000",
            font=("Courier", 10, "bold"), command=self.trigger_pipeline, relief=tk.FLAT,
            padx=25, pady=10, activebackground="#00CC55"
        )
        self.btn_launch.pack(side=tk.RIGHT)
        
        self.status_lbl = tk.Label(control_frame, text="● ENGINE STATE: IDLE", bg="#0a0a0a", fg="#00FFBB", font=("Courier", 10, "bold"))
        self.status_lbl.pack(side=tk.LEFT, pady=5)

    # ==========================================
    # COMPONENT LOGIC & TRANSACTION ROUTINES
    # ==========================================
    def add_target(self):
        url = self.target_input.get().strip()
        if url in ("", "Paste runtime URL path targets here..."):
            self.log_terminal("Manual target injection rejected: Empty string fields verified.", "warning")
            return
        if not (url.startswith("http://") or url.startswith("https://")):
            self.log_terminal("Injection fault: Missing explicit web schema prefix (http/https).", "error")
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO custom_targets (url, status) VALUES (?, ?)', (url, 'PENDING'))
            conn.commit()
            conn.close()
            
            self.target_input.delete(0, tk.END)
            self.target_input.insert(0, "Paste runtime URL path targets here...")
            self.log_terminal(f"Successfully injected dynamic queue tracking route: {url}", "success")
        except sqlite3.IntegrityError:
            self.log_terminal("VFS Reject: Target entry already allocated inside SQLite arrays.", "warning")
        except Exception as e:
            self.log_terminal(f"Target transaction lookup block failure: {e}", "error")

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Lists", "*.csv"), ("Raw Configuration Texts", "*.txt")])
        if not file_path:
            return
        
        def run_import():
            imported, duplicates, dropped = 0, 0, 0
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if not row: continue
                        url = row[0].strip()
                        if url.startswith("http://") or url.startswith("https://"):
                            try:
                                cursor.execute('INSERT INTO custom_targets (url, status) VALUES (?, ?)', (url, 'PENDING'))
                                imported += 1
                            except sqlite3.IntegrityError:
                                duplicates += 1
                        else:
                            dropped += 1
                conn.commit()
                conn.close()
                self.log_terminal(f"CSV Parse Completed: Injected {imported} nodes | Skipped {duplicates} dupes | Dropped {dropped} invalid targets", "success")
            except Exception as e:
                self.log_terminal(f"Structural import operation aborted: {e}", "error")
        threading.Thread(target=run_import, daemon=True).start()

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Document", "*.csv")])
        if not file_path:
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, timestamp, source_domain, title, status FROM ingestion_ledger ORDER BY id DESC")
            records = cursor.fetchall()
            conn.close()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Execution Timestamp", "Domain Context", "Extracted Identity Title", "Pipeline Output State"])
                writer.writerows(records)
            self.log_terminal(f"Database logs exported to file cleanly: {file_path}", "success")
        except Exception as e:
            self.log_terminal(f"Export task block error: {e}", "error")

    def clear_pending_targets(self):
        if messagebox.askyesno("Confirm Purge Actions", "Scrub all custom dynamic inputs currently flagged as PENDING?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM custom_targets WHERE status = 'PENDING'")
                conn.commit()
                conn.close()
                self.log_terminal("Purged dynamic custom targets database tracks to clear queues.", "warning")
            except Exception as e:
                self.log_terminal(f"Purge sequence error encountered: {e}", "error")

    def on_ledger_select(self, event):
        selected = self.ledger_tree.selection()
        if not selected:
            return
        item = self.ledger_tree.item(selected[0])
        try:
            row_id = int(item['values'][0])
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT target_url, summary FROM ingestion_ledger WHERE id = ?', (row_id,))
            record = cursor.fetchone()
            conn.close()
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete("1.0", tk.END)
            if record:
                url, summary = record
                self.detail_text.insert("1.0", f"SOURCE LOCATION ORIGIN URL: {url}\n" + "="*80 + f"\n\n{summary}")
                self.log_terminal(f"Inspecting payload transaction index identity: ID #{row_id}", "info")
            else:
                self.detail_text.insert("1.0", "Error: Missing document trace details inside table row paths.")
            self.detail_text.config(state=tk.DISABLED)
        except Exception as e:
            print(f"Detail selection event exception: {e}")

    def refresh_dashboard(self):
        if not os.path.exists(self.db_path):
            self.after(4000, self.refresh_dashboard)
            return
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch table log contents
            cursor.execute("SELECT id, timestamp, source_domain, title, status FROM ingestion_ledger ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            
            # Clean current row indexes
            selected_ids = [self.ledger_tree.item(x)['values'][0] for x in self.ledger_tree.selection()] if self.ledger_tree.selection() else []
            
            for item in self.ledger_tree.get_children():
                self.ledger_tree.delete(item)
                
            for row in rows:
                node_id = self.ledger_tree.insert("", tk.END, values=row)
                if row[0] in selected_ids:
                    self.ledger_tree.selection_set(node_id)
            
            # Extract core metrics telemetry points
            cursor.execute("SELECT metric_key, metric_value FROM telemetry")
            metrics = dict(cursor.fetchall())
            
            # Pull runtime error limits to dynamically flag component state indications
            cursor.execute("SELECT COUNT(*) FROM telemetry WHERE metric_key = 'anomaly_logged_event'")
            anomalies = cursor.fetchone()[0]
            conn.close()
            
            attempts = int(metrics.get("god_stack_ingestion_attempts_total", 0))
            successes = int(metrics.get("god_stack_ingestion_success_total", 0))
            
            self.lbl_attempts.config(text=str(attempts))
            self.lbl_successes.config(text=str(successes))
            
            if attempts > 0:
                acc_rate = (successes / attempts) * 100
                self.lbl_yield.config(text=f"{acc_rate:.1f}%")
                
                # Check for active circuit breaker or limiter backpressure alerts
                if acc_rate < 70.0 or anomalies > 5:
                    self.state_labels["Circuit Breaker"].config(text="OPEN [BACKOFF ALERT]", fg="#FF3333")
                    self.state_labels["Rate Limiter"].config(text="PRESSURE BACKOFF ENFORCED", fg="#FFCC00")
                else:
                    self.state_labels["Circuit Breaker"].config(text="CLOSED (STABLE)", fg="#00FFBB")
                    self.state_labels["Rate Limiter"].config(text="SLIDING WINDOW (10 rps)", fg="#00FFBB")
            else:
                self.lbl_yield.config(text="0.0%")
                
        except Exception as e:
            pass
        self.after(4000, self.refresh_dashboard)

    def trigger_pipeline(self):
        self.btn_launch.config(state="disabled", bg="#222222", text="EXECUTING PROCESS ENGINES...")
        self.status_lbl.config(text="● ENGINE STATE: ACTIVE PIPELINE RUNNING", fg="#FFCC00")
        self.log_terminal("Instantiating sub-thread process allocation running core orchestrator framework", "warning")
        
        def run():
            try:
                # Trigger orchestrator executable mapping tracking
                res = subprocess.run([sys.executable, "/home/tangleroot013/god_stack/orchestrator.py"], capture_output=True, text=True, check=True)
                
                # Dump internal process print sequences right down to our log panel
                for line in res.stdout.splitlines():
                    if "worker_node" in line or "Final" in line or "System" in line:
                        self.after(0, lambda l=line: self.log_terminal(l.split("|")[-1].strip(), "info"))
                
                self.after(0, lambda: self.log_terminal("Pipeline routine run finished cleanly. System sync finalized.", "success"))
            except subprocess.CalledProcessError as err:
                self.after(0, lambda e=err: self.log_terminal(f"Core Engine Execution Fault: {e.stderr if e.stderr else e}", "error"))
                self.after(0, lambda e=err: messagebox.showerror("Pipeline Execution Core Failure", f"Subprocess matrix thrown an unhandled exception layer:\n{e.stderr}"))
            except Exception as ex:
                self.after(0, lambda e=ex: self.log_terminal(f"Process transport fatal layer error: {e}", "error"))
            finally:
                self.after(0, self.reset_control_strip)
        threading.Thread(target=run, daemon=True).start()

    def reset_control_strip(self):
        self.btn_launch.config(state="normal", bg="#00FF66", text="⚡ EXECUTE PIPELINE MATRIX")
        self.status_lbl.config(text="● ENGINE STATE: IDLE", fg="#00FFBB")
        self.refresh_dashboard()

if __name__ == "__main__":
    app = GodStackDashboard()
    app.mainloop()
