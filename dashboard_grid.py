#!/usr/bin/env python3
"""
G.O.D. STACK V2.0 - OPERATIONAL DATA CONTROL PLATFORM
Fully integrated dashboard layout mapping custom targets and live payload verification readouts.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import sys
import threading
import os

class GodStackDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("G.O.D. STACK — CORE ENGINE OPERATIONAL MONITOR")
        self.geometry("1100x750")
        self.configure(bg="#121212")
        
        self.db_path = "/home/tangleroot013/god_stack/god_stack_vfs.db"
        self.init_custom_targets_table()
        
        # Main layout frame container mapping layout padding cleanly
        self.main_frame = tk.Frame(self, bg="#121212", padx=15, pady=15)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Build layout elements sequentially inside the system grid
        self.create_injection_frame()
        self.create_header()
        self.create_kpi_panel()
        self.create_ledger_grid()
        self.create_detail_panel()
        self.create_control_bar()
        
        # Initialize internal monitoring loops
        self.refresh_dashboard()

    def init_custom_targets_table(self):
        """Initializes database schema layers for the target routing configuration indices."""
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
            print(f"VFS Storage Matrix Subsystem Warning: {e}")

    def create_injection_frame(self):
        """Builds the dynamic horizontal URL injector bar matrix."""
        injection_frame = tk.Frame(self.main_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1, padx=10, pady=8)
        injection_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        lbl_inject = tk.Label(
            injection_frame, 
            text="DYNAMIC TARGET INJECTOR", 
            bg="#FF6B00", 
            fg="#000000", 
            font=("Courier", 9, "bold"),
            padx=8
        )
        lbl_inject.pack(side=tk.LEFT, padx=(0, 10))
        
        self.target_input = tk.Entry(
            injection_frame, 
            bg="#1a1a1a", 
            fg="#666666", 
            font=("Courier", 10), 
            relief=tk.FLAT,
            insertbackground="#00FF66",
            bd=5
        )
        self.target_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.target_input.insert(0, "Paste target URL here...")
        
        def on_focus_in(event):
            if self.target_input.get() == "Paste target URL here...":
                self.target_input.delete(0, tk.END)
                self.target_input.config(fg="#00FF66")
        
        def on_focus_out(event):
            if self.target_input.get() == "":
                self.target_input.insert(0, "Paste target URL here...")
                self.target_input.config(fg="#666666")
        
        self.target_input.bind("<FocusIn>", on_focus_in)
        self.target_input.bind("<FocusOut>", on_focus_out)
        
        self.inject_btn = tk.Button(
            injection_frame, 
            text="➕ ADD TARGET", 
            bg="#FF6B00", 
            fg="#000000", 
            font=("Courier", 9, "bold"),
            command=self.add_target,
            relief=tk.FLAT,
            padx=15,
            activebackground="#FF8C00"
        )
        self.inject_btn.pack(side=tk.RIGHT)

    def add_target(self):
        """Commits newly injected entry metrics inside persistent VFS index maps."""
        url = self.target_input.get().strip()
        if url in ("", "Paste target URL here..."):
            messagebox.showwarning("Validation Warning", "Specified extraction destination context cannot remain blank.")
            return
        
        if not (url.startswith("http://") or url.startswith("https://")):
            messagebox.showerror("Validation Structural Failure", "Extraction vectors must conform strictly to standard http:// or https:// structural pathways.")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO custom_targets (url, status) VALUES (?, ?)', (url, 'PENDING'))
            conn.commit()
            conn.close()
            
            self.target_input.delete(0, tk.END)
            self.target_input.insert(0, "Paste target URL here...")
            self.target_input.config(fg="#666666")
            messagebox.showinfo("Matrix Synchronized", f"Registered entry node successfully loaded to engine scope:\n{url}")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Duplication Trap", "The target network path requested already exists within execution indexing arrays.")
        except Exception as e:
            messagebox.showerror("VFS Transaction Core Fault", f"Failed to preserve requested context array mapping: {e}")

    def create_header(self):
        header_frame = tk.Frame(self.main_frame, bg="#121212")
        header_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        lbl_title = tk.Label(
            header_frame,
            text="CORE ENGINE OPERATIONAL MONITOR",
            bg="#121212",
            fg="#00FF66",
            font=("Courier", 15, "bold")
        )
        lbl_title.pack(side=tk.LEFT, pady=5)
        
        self.status_indicator = tk.Label(
            header_frame,
            text="● SYSTEM IDLE",
            bg="#121212",
            fg="#00FFBB",
            font=("Courier", 11, "bold")
        )
        self.status_indicator.pack(side=tk.RIGHT, pady=5)

    def create_kpi_panel(self):
        kpi_frame = tk.Frame(self.main_frame, bg="#121212")
        kpi_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))
        
        # Configure layout distribution weights
        kpi_frame.grid_columnconfigure(0, weight=1)
        kpi_frame.grid_columnconfigure(1, weight=1)
        kpi_frame.grid_columnconfigure(2, weight=1)
        
        # Card 1: Intake Metrics
        card1 = tk.Frame(kpi_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1, padx=10, pady=8)
        card1.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        tk.Label(card1, text="ATTEMPTS LOGGED", bg="#00E5FF", fg="#000000", font=("Courier", 8, "bold"), padx=5).pack(anchor="w")
        self.lbl_attempts = tk.Label(card1, text="0", bg="#0d0d0d", fg="#FFFFFF", font=("Courier", 20, "bold"))
        self.lbl_attempts.pack(anchor="w", pady=(5, 0))
        
        # Card 2: Integrity Verification Metrics
        card2 = tk.Frame(kpi_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1, padx=10, pady=8)
        card2.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Label(card2, text="VERIFIED SUCCESSES", bg="#00FF66", fg="#000000", font=("Courier", 8, "bold"), padx=5).pack(anchor="w")
        self.lbl_successes = tk.Label(card2, text="0", bg="#0d0d0d", fg="#00FF66", font=("Courier", 20, "bold"))
        self.lbl_successes.pack(anchor="w", pady=(5, 0))
        
        # Card 3: System Extraction Accuracy Metrics
        card3 = tk.Frame(kpi_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1, padx=10, pady=8)
        card3.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        tk.Label(card3, text="INGESTION ACCURACY", bg="#FFCC00", fg="#000000", font=("Courier", 8, "bold"), padx=5).pack(anchor="w")
        self.lbl_yield = tk.Label(card3, text="0.0%", bg="#0d0d0d", fg="#FFCC00", font=("Courier", 20, "bold"))
        self.lbl_yield.pack(anchor="w", pady=(5, 0))

    def create_ledger_grid(self):
        ledger_label = tk.Label(self.main_frame, text="TRANSACTION INGESTION LEDGER MATRIX", bg="#121212", fg="#00FF66", font=("Courier", 9, "bold"), anchor="w")
        ledger_label.pack(fill=tk.X, side=tk.TOP, pady=(5, 2))
        
        ledger_frame = tk.Frame(self.main_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1)
        ledger_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        scrollbar = ttk.Scrollbar(ledger_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.ledger_tree = ttk.Treeview(
            ledger_frame,
            columns=("IDX", "TIMESTAMP", "SOURCE DOMAIN", "EXTRACTION TYPE", "CRYPTO STATUS"),
            height=7,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.ledger_tree.yview)
        
        self.ledger_tree.heading("#0", text="")
        self.ledger_tree.column("#0", width=0, minwidth=0, stretch=tk.NO)
        self.ledger_tree.heading("IDX", text="IDX")
        self.ledger_tree.column("IDX", width=50, anchor="center", stretch=tk.NO)
        self.ledger_tree.heading("TIMESTAMP", text="TIMESTAMP")
        self.ledger_tree.column("TIMESTAMP", width=160, anchor="center")
        self.ledger_tree.heading("SOURCE DOMAIN", text="SOURCE DOMAIN")
        self.ledger_tree.column("SOURCE DOMAIN", width=180, anchor="w")
        self.ledger_tree.heading("EXTRACTION TYPE", text="EXTRACTION TYPE")
        self.ledger_tree.column("EXTRACTION TYPE", width=220, anchor="w")
        self.ledger_tree.heading("CRYPTO STATUS", text="CRYPTO STATUS")
        self.ledger_tree.column("CRYPTO STATUS", width=200, anchor="center")
        
        self.ledger_tree.pack(fill=tk.BOTH, expand=True)
        
        # Configure custom display layout mappings
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview", background="#0d0d0d", foreground="#00FF66", fieldbackground="#0d0d0d", font=("Courier", 9), rowheight=24)
        style.configure("Treeview.Heading", background="#1a1a1a", foreground="#00E5FF", font=("Courier", 9, "bold"))
        style.map("Treeview", background=[('selected', '#1a1a1a')], foreground=[('selected', '#FF6B00')])
        
        self.ledger_tree.bind('<<TreeviewSelect>>', self.on_ledger_select)

    def create_detail_panel(self):
        """Constructs the text stream window to map payload data extracts visually."""
        detail_label = tk.Label(self.main_frame, text="LIVE VERIFIED PAYLOAD STREAM READOUT", bg="#121212", fg="#00FF66", font=("Courier", 9, "bold"), anchor="w")
        detail_label.pack(fill=tk.X, side=tk.TOP, pady=(10, 2))
        
        detail_frame = tk.Frame(self.main_frame, bg="#0d0d0d", relief=tk.SUNKEN, bd=1)
        detail_frame.pack(fill=tk.BOTH, expand=True, side=tk.TOP, pady=(0, 10))
        
        self.detail_text = tk.Text(
            detail_frame,
            bg="#0d0d0d",
            fg="#00E5FF",
            font=("Courier", 9),
            wrap=tk.WORD,
            relief=tk.FLAT,
            insertbackground="#00FF66",
            padx=10,
            pady=10
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        self.detail_text.insert("1.0", "[System Idle] Highlight an ingestion transaction inside the ledger index to analyze runtime verification payloads...")
        self.detail_text.config(state=tk.DISABLED)

    def on_ledger_select(self, event):
        """Binds click selection matrices back to targeted table lookups."""
        selected = self.ledger_tree.selection()
        if not selected:
            return
            
        item = self.ledger_tree.item(selected[0])
        try:
            row_id = int(item['values'][0])
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT target_url, summary FROM ingestion_ledger WHERE id = ?', (row_id,))
            result = cursor.fetchone()
            conn.close()
            
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete("1.0", tk.END)
            if result:
                url, summary = result
                formatted_payload = f"ORIGIN SOURCE RECON: {url}\n" + "="*70 + f"\n\n{summary}"
                self.detail_text.insert("1.0", formatted_payload)
            else:
                self.detail_text.insert("1.0", "Selected transaction does not point to valid content data layers.")
            self.detail_text.config(state=tk.DISABLED)
        except Exception as e:
            self.detail_text.config(state=tk.NORMAL)
            self.detail_text.delete("1.0", tk.END)
            self.detail_text.insert("1.0", f"Error extracting payload stream metrics: {e}")
            self.detail_text.config(state=tk.DISABLED)

    def create_control_bar(self):
        control_frame = tk.Frame(self.main_frame, bg="#121212")
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.btn_launch = tk.Button(
            control_frame,
            text="⚡ EXECUTE PIPELINE MATRIX",
            bg="#00FF66",
            fg="#000000",
            font=("Courier", 10, "bold"),
            command=self.trigger_pipeline,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            activebackground="#00CC55"
        )
        self.btn_launch.pack(side=tk.RIGHT)
        
        btn_refresh = tk.Button(
            control_frame,
            text="🔄 REFRESH LEDGER",
            bg="#2a2a2a",
            fg="#FFFFFF",
            font=("Courier", 10, "bold"),
            command=self.refresh_dashboard,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            activebackground="#3a3a3a"
        )
        btn_refresh.pack(side=tk.LEFT)

    def refresh_dashboard(self):
        if not os.path.exists(self.db_path):
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fetch table rows
            cursor.execute("SELECT id, timestamp, source_domain, title, status FROM ingestion_ledger ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            
            # Refresh tree records without losing scroll perspective maps entirely
            selected_items = self.ledger_tree.selection()
            selected_idx = self.ledger_tree.item(selected_items[0])['values'][0] if selected_items else None
            
            for item in self.ledger_tree.get_children():
                self.ledger_tree.delete(item)
                
            for row in rows:
                inserted_item = self.ledger_tree.insert("", tk.END, values=row)
                if selected_idx and row[0] == selected_idx:
                    self.ledger_tree.selection_set(inserted_item)
            
            # Update telemetry layout displays
            cursor.execute("SELECT metric_key, metric_value FROM telemetry")
            metrics = dict(cursor.fetchall())
            conn.close()
            
            attempts = int(metrics.get("god_stack_ingestion_attempts_total", 0))
            successes = int(metrics.get("god_stack_ingestion_success_total", 0))
            
            self.lbl_attempts.config(text=str(attempts))
            self.lbl_successes.config(text=str(successes))
            
            if attempts > 0:
                accuracy_pct = (successes / attempts) * 100
                self.lbl_yield.config(text=f"{accuracy_pct:.1f}%")
            else:
                self.lbl_yield.config(text="0.0%")
                
        except Exception as e:
            print(f"Transient system VFS lookup block collision: {e}")
            
        self.after(3000, self.refresh_dashboard)

    def trigger_pipeline(self):
        self.btn_launch.config(state="disabled", bg="#444444", text="PROCESSING...")
        self.status_indicator.config(text="● PIPELINE ACTIVE", fg="#FFCC00")
        
        def run():
            try:
                subprocess.run([sys.executable, "/home/tangleroot013/god_stack/orchestrator.py"], check=True)
            except Exception as ex:
                self.after(0, lambda: messagebox.showerror("Pipeline Fault", f"Execution transport error: {ex}"))
            finally:
                self.after(0, self.reset_trigger_button)
                
        threading.Thread(target=run, daemon=True).start()

    def reset_trigger_button(self):
        self.btn_launch.config(state="normal", bg="#00FF66", text="⚡ EXECUTE PIPELINE MATRIX")
        self.status_indicator.config(text="● SYSTEM IDLE", fg="#00FFBB")
        self.refresh_dashboard()

if __name__ == "__main__":
    app = GodStackDashboard()
    app.mainloop()
