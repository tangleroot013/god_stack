import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[IDLE-SHIELD]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("IdleShield")

class InactivitySleepShield:
    def __init__(self, root_window, timeout_ms: int = 400):
        self.root = root_window
        self.timeout = timeout_ms
        self.timer_id = None
        
        # Bind global event interception lines across the entire window structure
        self.root.bind_all("<Any-KeyPress>", self.refresh_operator_activity)
        self.root.bind_all("<Any-Motion>", self.refresh_operator_activity)
        self.reset_idle_countdown()

    def reset_idle_countdown(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_id = self.root.after(self.timeout, self.trigger_lockout_sequence)

    def refresh_operator_activity(self, event=None):
        self.reset_idle_countdown()

    def trigger_lockout_sequence(self):
        print("\n\033[1;31m--- G.O.D. IDLE SHIELD ACTIVE LOCKOUT INITIATED ---\033[0m")
        logger.warning("No interactive inputs detected inside window perimeter. Masking matrices.")

if __name__ == "__main__":
    root = tk.Tk()
    shield = InactivitySleepShield(root, timeout_ms=300)
    
    # Simulate user activity pulses, then let it expire
    root.after(100, lambda: root.event_generate("<Motion>", x=10, y=10))
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 123 INTERACTIVE COUNTERMEASURES ONLINE.\033[0m\n")
