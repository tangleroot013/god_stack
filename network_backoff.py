import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[BACKOFF-TRACK]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("BackoffTrack")

class NetworkBackoffWidget:
    def __init__(self, root_window):
        self.label = tk.Label(root_window, text="NET LINK: ESTABLISHED", bg="#002200", fg="#00ff00", font=("Courier", 9))
        self.label.pack(fill="x", padx=10, pady=2)

    def signal_link_failure(self, current_retry: int, next_delay_sec: float):
        print("\n\033[1;32m--- G.O.D. DOWNSTREAM ROUTE FAULT TRACE ---\033[0m")
        logger.warning(f"Connection dropped. Scheduling retry step [{current_retry}] in {next_delay_sec}s")
        self.label.config(
            text=f"LINK FAULT // RETRY SEQUENCE #{current_retry} IN {next_delay_sec:.1f}s", 
            bg="#330000", 
            fg="#ff3333"
        )

if __name__ == "__main__":
    root = tk.Tk()
    tracker = NetworkBackoffWidget(root)
    
    # Simulate a circuit route drop signal
    root.after(100, lambda: tracker.signal_link_failure(current_retry=3, next_delay_sec=4.5))
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 124 ASYNC CONNECTION MONITOR STABLE.\033[0m\n")
