#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox, filedialog
import asyncio
import threading
import csv
import os
import time
from datetime import datetime

# Core imports
from god_engine import GodEngineNode
from god_scraper import GodScraper

# Upgrade Framework imports
from engine_extension_core import DynamicRateLimiter, DataSanitizer, PayloadLedger

class GodStackBatchGui:
    def __init__(self, root):
        self.root = root
        self.root.title("G.O.D. STACK | Enhanced Extraction Suite")
        self.root.geometry("800x580")
        self.root.configure(bg="#111115")
        
        self.loop = asyncio.new_event_loop()
        self.threading_worker = None

        self._build_ui_layout()

    def _build_ui_layout(self):
        # Header banner styling
        header = tk.Label(
            self.root, 
            text="G.O.D. STACK v3.0 | EXTENSION MATRIX HARNESS", 
            font=("Courier", 13, "bold"), 
            bg="#111115", 
            fg="#00ff66"
        )
        header.pack(pady=10)

        # Content Frame
        main_frame = tk.Frame(self.root, bg="#111115")
        main_frame.pack(padx=20, pady=5, fill=tk.BOTH, expand=True)

        lbl = tk.Label(main_frame, text="Target URL Buffer Array:", font=("Arial", 10), bg="#111115", fg="#8e8e93")
        lbl.pack(anchor="w")

        self.text_area = tk.Text(
            main_frame, 
            height=12, 
            bg="#1c1c1e", 
            fg="#ffffff", 
            insertbackground="#00ff66",
            font=("Consolas", 10),
            bd=0,
            highlightthickness=1,
            highlightbackground="#2c2c2e"
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        self.text_area.insert(tk.END, "https://example.com/stream_node_v2_0\nhttps://example.com/stream_node_v2_0\nhttps://example.com/stream_node_v2_1")

        # Interactive Log view terminal panel
        self.console_status = tk.Label(
            self.root,
            text="STATUS: Middleware Engines Armed. Ready for deployment pipeline loop.",
            font=("Courier", 9, "bold"),
            bg="#1c1c1e",
            fg="#00bcff",
            anchor="w",
            padx=10,
            pady=8
        )
        self.console_status.pack(fill=tk.X, padx=20, pady=5)

        # Command Button Matrix Panel
        btn_frame = tk.Frame(self.root, bg="#111115")
        btn_frame.pack(pady=15)

        self.btn_run = tk.Button(
            btn_frame, 
            text="EXECUTE PRODUCTION STACK", 
            command=self.start_batch_processing, 
            bg="#00ff66", 
            fg="#000000", 
            font=("Arial", 10, "bold"),
            padx=15,
            pady=6,
            bd=0,
            cursor="hand2"
        )
        self.btn_run.pack(side=tk.LEFT, padx=10)

        self.btn_clear = tk.Button(
            btn_frame, 
            text="RESET BUFFER", 
            command=lambda: self.text_area.delete("1.0", tk.END), 
            bg="#2c2c2e", 
            fg="#ffffff", 
            font=("Arial", 10),
            padx=10,
            pady=6,
            bd=0,
            cursor="hand2"
        )
        self.btn_clear.pack(side=tk.LEFT, padx=10)

    def log_status(self, text, color="#ffffff"):
        self.console_status.config(text=f"SYSTEM: {text}", fg=color)
        self.root.update_idletasks()

    def start_batch_processing(self):
        raw_input = self.text_area.get("1.0", tk.END).strip()
        urls = [url.strip() for url in raw_input.split("\n") if url.strip()]

        if not urls:
            messagebox.showwarning("Empty Target Matrix", "Tracking route queue is currently vacant.")
            return

        self.btn_run.config(state=tk.DISABLED)
        self.threading_worker = threading.Thread(target=self._async_thread_worker, args=(urls,), daemon=True)
        self.threading_worker.start()

    def _async_thread_worker(self, urls):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._process_matrix_pipeline(urls))

    async def _process_matrix_pipeline(self, urls):
        results_dataset = []
        
        # Instantiate upgrade engines locally inside parsing loop scope
        limiter = DynamicRateLimiter()
        sanitizer = DataSanitizer()
        ledger = PayloadLedger()

        try:
            self.log_status("Spinning engine context frameworks...", "#bc00ff")
            await GodEngineNode.initialize(headless=True)
            
            total_targets = len(urls)
            for index, url in enumerate(urls, start=1):
                
                # Check Module 3: PayloadLedger Duplicate Bypass Hook
                if ledger.is_duplicate(url):
                    print(f"[UI MATRIX ALERT] Deduplicated target link footprint skipped: {url}")
                    continue

                # Check Module 1: Throttle Request Delay Footprint
                self.log_status(f"Enforcing Adaptive Backoff ({limiter.current_delay:.2f}s delay window)...", "#ffcc00")
                await limiter.throttle()

                self.log_status(f"Ingesting node ({index}/{total_targets}): {url}...", "#ffcc00")
                
                start_time = time.perf_counter()
                frame = await GodEngineNode.fetch_and_extract(url)
                latency_ms = int((time.perf_counter() - start_time) * 1000)

                # Dynamically calculate adaptive pacing velocity based on response clock latency
                limiter.adjust_velocity(latency_ms)
                
                if frame["status"] == "SUCCESS":
                    # Check Module 2: Apply Clean String Data Sanitizer Filters
                    raw_title = frame["extracted_data"]["title"]
                    polished_title = sanitizer.clean_string(raw_title)

                    results_dataset.append({
                        "URL": url,
                        "Status": "SUCCESS",
                        "Title": polished_title,
                        "Bytes Recieved": frame["metrics"]["payload_bytes"],
                        "Links Discovered": frame["metrics"]["discovered_anchors_count"],
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                else:
                    results_dataset.append({
                        "URL": url,
                        "Status": "FAILED",
                        "Title": "N/A",
                        "Bytes Recieved": 0,
                        "Links Discovered": 0,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            await GodEngineNode.shutdown()
            self.root.after(0, self._export_to_csv, results_dataset)

        except Exception as e:
            self.root.after(0, lambda err=e: self._handle_failure(err))

    def _export_to_csv(self, dataset):
        if not dataset:
            messagebox.showinfo("Processing Cycle Concluded", "All input targets mapped to existing cache signatures. No new CSV records needed.")
            self.btn_run.config(state=tk.NORMAL)
            self.log_status("System Idle. Matrix up-to-date.", "#00ff66")
            return

        self.log_status("Generating secure output spreadsheet matrices...", "#00ff66")
        
        # Point dialog natively towards the safe write workspace outputs directory 
        default_dir = os.path.join(os.getcwd(), "outputs")
        export_filepath = filedialog.asksaveasfilename(
            initialdir=default_dir,
            title="Save Production CSV Matrix",
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv")]
        )

        if not export_filepath:
            export_filepath = os.path.join(default_dir, "god_stack_extraction_matrix.csv")

        try:
            fields = ["URL", "Status", "Title", "Bytes Recieved", "Links Discovered", "Timestamp"]
            with open(export_filepath, mode="w", newline="", encoding="utf-8") as target_file:
                writer = csv.DictWriter(target_file, fieldnames=fields)
                writer.writeheader()
                writer.writerows(dataset)

            messagebox.showinfo(
                "Ingestion Engine Matrix Saved", 
                f"Data telemetry mapped cleanly to target:\n\n{export_filepath}"
            )
        except Exception as csv_err:
            messagebox.showerror("IO Export Mutation Fault", f"Could not write file: {csv_err}")

        self.btn_run.config(state=tk.NORMAL)
        self.log_status("System Idle. Complete operational run records exported.", "#00ff66")

    def _handle_failure(self, error):
        messagebox.showerror("Processing Interruption Fault", f"Error occurred: {error}")
        self.btn_run.config(state=tk.NORMAL)
        self.log_status("Error context caught. Realignment standing by.", "#ff3333")

if __name__ == "__main__":
    app_root = tk.Tk()
    app = GodStackBatchGui(app_root)
    app_root.mainloop()
