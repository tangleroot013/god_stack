import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;36m%(asctime)s\033[0m | \033[1;34m[UI-WATCHDOG]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("UIWatchdog")

class VisualKeepaliveIndicator:
    def __init__(self, root_window):
        self.root = root_window
        self.status_bar = tk.Label(root_window, text="UI LOOP: STANDBY", bg="#111111", fg="#ffffff", font=("Courier", 9))
        self.status_bar.pack(fill="x", side="bottom")
        self.tick_state = False

    def initiate_heartbeat_loop(self):
        # Toggle a dynamic structural heartbeat state to prove event-loop responsiveness
        self.tick_state = not self.tick_state
        indicator = "[⚡]" if self.tick_state else "[ ]"
        
        self.status_bar.config(text=f"CORE EVENT LOOP RESPONSE STATUS: NOMINAL {indicator}", fg="#00ff00" if self.tick_state else "#00aa00")
        logger.info(f"UI Thread Activity Tick: {indicator} Event loop clear.")
        
        # Re-queue the heartbeat task into the Tkinter window event manager loop
        self.root.after(200, self.initiate_heartbeat_loop)

if __name__ == "__main__":
    print("\n\033[1;32m--- G.O.D. ASYNC RENDER MATRIX HEALTH INTERFACE ---\033[0m")
    root = tk.Tk()
    root.geometry("300x50")
    watchdog = VisualKeepaliveIndicator(root)
    
    root.after(50, watchdog.initiate_heartbeat_loop)
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 112 GUI RENDER TRACKING TICK ACTIVE.\033[0m\n")
