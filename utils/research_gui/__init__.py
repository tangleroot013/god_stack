import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import urllib.request
import urllib.error
import time
from pathlib import Path

class GodResearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GOD Stack Research Builder [PROD]")
        self.root.geometry("700x600")
        self.root.minsize(550, 450)
        
        # Clean modern cross-platform typography mapping
        self.font_family = "TkDefaultFont"
        self.mono_family = "Courier" if root.tk.call("tk", "windowingsystem") == "aqua" else "monospace"
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Thread tracking setup for graceful handling
        self.active_threads = []
        self.is_shutting_down = False
        self.root.protocol("WM_DELETE_WINDOW", self.graceful_shutdown)
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header Label
        header_lbl = ttk.Label(main_frame, text="🚀 GOD Research Injection Node", font=(self.font_family, 14, "bold"))
        header_lbl.pack(anchor=tk.W, pady=(0, 15))
        
        # Mode Selection Matrix
        mode_frame = ttk.LabelFrame(main_frame, text=" Input Matrix Mode ", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_mode = tk.StringVar(value="keywords")
        rb_prio = ttk.Radiobutton(mode_frame, text="Target Keywords / Phrases", variable=self.input_mode, value="keywords")
        rb_url = ttk.Radiobutton(mode_frame, text="Direct Target URLs", variable=self.input_mode, value="urls")
        rb_prio.pack(side=tk.LEFT, padx=10)
        rb_url.pack(side=tk.LEFT, padx=10)
        
        # Data Stream Frame
        input_label_frame = ttk.LabelFrame(main_frame, text=" Entry Stream (Lines starting with # are ignored) ", padding="10")
        input_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_input = tk.Text(input_label_frame, wrap=tk.WORD, font=(self.mono_family, 10), undo=True)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # Advanced Execution Modifiers
        modifier_frame = ttk.Frame(input_label_frame)
        modifier_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.is_priority = tk.BooleanVar(value=False)
        cb_priority = ttk.Checkbutton(modifier_frame, text="Escalate to Priority Lane Execution Ceiling", variable=self.is_priority)
        cb_priority.pack(side=tk.LEFT, anchor=tk.W)
        
        self.clear_on_success = tk.BooleanVar(value=False)
        cb_clear = ttk.Checkbutton(modifier_frame, text="Auto-clear window on successful dispatch", variable=self.clear_on_success)
        cb_clear.pack(side=tk.RIGHT, anchor=tk.E)
        
        # Execution Controls
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 10))
        
        self.submit_btn = ttk.Button(btn_frame, text="Dispatch to GOD Ingress Mesh", command=self.start_dispatch_thread)
        self.submit_btn.pack(side=tk.RIGHT, padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="Clear Window", command=lambda: self.text_input.delete("1.0", tk.END))
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Telemetry & Status Strips
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.status_lbl = ttk.Label(main_frame, text="Status: Node Ready", font=(self.font_family, 10, "italic"))
        self.status_lbl.pack(anchor=tk.W)

    def set_ui_state(self, active=True):
        if active:
            self.submit_btn.config(state=tk.NORMAL)
            self.clear_btn.config(state=tk.NORMAL)
            self.text_input.config(state=tk.NORMAL)
            self.progress_bar.pack_forget()
        else:
            self.submit_btn.config(state=tk.DISABLED)
            self.clear_btn.config(state=tk.DISABLED)
            self.text_input.config(state=tk.DISABLED)
            self.progress_bar.pack(fill=tk.X, pady=(0, 5))
            self.progress_bar.start(10)

    def start_dispatch_thread(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Empty Target Matrix", "Please specify at least one keyword payload or website parameter target.")
            return
            
        # Parse text array line-by-line while filtering blank entries AND inline comments
        entries = [
            line.strip() for line in raw_text.split("\n") 
            if line.strip() and not line.lstrip().startswith("#")
        ]
        
        if not entries:
            messagebox.showwarning("No Active Targets", "All entries provided were parsed as system comments or blank lines.")
            return
            
        t = threading.Thread(target=self.dispatch_payloads, args=(entries,), daemon=True)
        self.active_threads.append(t)
        t.start()

    def dispatch_payloads(self, entries):
        self.set_ui_state(False)
        mode = self.input_mode.get()
        priority_flag = self.is_priority.get()
        
        success_count = 0
        backpressure_count = 0
        network_fail_count = 0
        
        run_results_log = []
        target_url = "http://127.0.0.1:8090/ingest"
        
        for item in entries:
            if self.is_shutting_down:
                break
                
            self.status_lbl.config(text=f"Status: Ingesting target reference -> '{item}'...")
            
            payload = {
                "type": mode,
                "target": item,
                "priority": priority_flag,
                "client_timestamp": time.time()
            }
            
            log_entry = {"target": item, "timestamp": time.time(), "status": None, "error_reason": None}
            
            try:
                req_data = json.dumps(payload).encode('utf-8')
                req = urllib.request.Request(
                    target_url, 
                    data=req_data, 
                    headers={'Content-Type': 'application/json'}
                )
                
                # Elevated 10-second request timeout boundary 
                with urllib.request.urlopen(req, timeout=10) as response:
                    log_entry["status"] = response.status
                    if response.status in [200, 202]:
                        success_count += 1
                    else:
                        network_fail_count += 1
            except urllib.error.HTTPError as e:
                log_entry["status"] = e.code
                log_entry["error_reason"] = f"HTTP Error Server Response: {e.reason}"
                if e.code == 503:
                    backpressure_count += 1
                else:
                    network_fail_count += 1
            except urllib.error.URLError as e:
                log_entry["status"] = "CONNECTION_REFUSED"
                log_entry["error_reason"] = str(e.reason)
                network_fail_count += 1
            except Exception as e:
                log_entry["status"] = "UNEXPECTED_INTERNAL_ERR"
                log_entry["error_reason"] = str(e)
                network_fail_count += 1
            finally:
                run_results_log.append(log_entry)
                # 50ms pacing safety delay to prevent loop execution lockups
                time.sleep(0.05)
                
        # Post-Run Analysis Dump Execution
        try:
            log_dir = Path("vaults")
            log_dir.mkdir(exist_ok=True)
            with open(log_dir / "dispatch_analysis_log.json", "w") as f:
                json.dump(run_results_log, f, indent=2)
        except Exception:
            pass # Guarantee UI response flow even if disk space is fully locked

        if self.is_shutting_down:

            return

        self.set_ui_state(True)
        self.status_lbl.config(
            text=f"Status: Done. 202 Success: {success_count} | 503 Sheds: {backpressure_count} | Drop Failures: {network_fail_count}"
        )
        
        # Process interface clear flag preferences
        if success_count == len(entries) and self.clear_on_success.get():
            self.text_input.delete("1.0", tk.END)

        # Build notification alert modals based on granular findings
        if network_fail_count == 0 and backpressure_count == 0:
            messagebox.showinfo("Transmission Complete", f"All {success_count} payloads successfully integrated into the cluster pipeline.")
        elif backpressure_count > 0:
            messagebox.showwarning(
                "Backpressure Tripped", 
                f"Dispatched: {success_count}. Rejected via 503 Shedding: {backpressure_count}.\n\nCluster lane depth saturation limits exceeded. Check vaults/dispatch_analysis_log.json for analysis."
            )
        else:
            messagebox.showerror(
                "Pipeline Execution Failure", 
                f"Failed connection attempts encountered during transmission.\nSuccesses: {success_count}\nFailures: {network_fail_count}"
            )

    def graceful_shutdown(self):
        self.is_shutting_down = True
        self.status_lbl.config(text="Status: Shutting down interface matrix...")
        # Await clean termination loop on background socket transfers
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GodResearchGUI(root)
    root.mainloop()
