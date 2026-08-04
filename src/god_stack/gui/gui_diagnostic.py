import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[DIAG-HUD]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DiagHUD")

class EphemeralDiagnosticOverlay:
    def __init__(self, root_window):
        self.root = root_window
        self.hud_window = None
        
        # Bind global hotkey sequence (Control + d) to manage overlay visibility
        self.root.bind_all("<Control-d>", self.toggle_hud_state)

    def toggle_hud_state(self, event=None):
        print("\n\033[1;32m--- G.O.D. DIAGNOSTIC VIEWPORT TRANSITION ---\033[0m")
        if self.hud_window is None or not tk.Toplevel.winfo_exists(self.hud_window):
            # Spawn isolated overlay layer
            self.hud_window = tk.Toplevel(self.root)
            self.hud_window.title("G.O.D. // Internal Engine Diagnostics")
            self.hud_window.geometry("300x150")
            self.hud_window.configure(bg="#050505")
            
            lbl = tk.Label(self.hud_window, text="DIAGNOSTIC ENVELOPE: ACTIVE\nASYNC_THREADS: 4\nRING_BUFF_ERR: 0", 
                           bg="#050505", fg="#00ffcc", font=("Courier", 10))
            lbl.pack(expand=True, fill="both")
            logger.info("Ephemeral diagnostic layout drawn onto active display pipeline.")
        else:
            # Complete teardown of HUD component allocation
            self.hud_window.destroy()
            self.hud_window = None
            logger.warning("Diagnostic envelope destroyed. Viewport context cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    hud = EphemeralDiagnosticOverlay(root)
    
    # Simulate manual trigger keys
    root.after(100, lambda: root.event_generate("<Control-d>")) # Open
    root.after(300, lambda: root.event_generate("<Control-d>")) # Close
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 120 DIAGNOSTIC COUPLING ACTIVE.\033[0m\n")
