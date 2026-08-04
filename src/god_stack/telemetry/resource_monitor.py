import tkinter as tk
import logging
import random

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[RESOURCE-MON]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ResourceMon")

class CanvasResourceMeter:
    def __init__(self, root_window):
        self.canvas = tk.Canvas(root_window, width=200, height=20, bg="#111111", highlightthickness=0)
        self.canvas.pack(padx=10, pady=5)
        # Draw base background tracking trough
        self.canvas.create_rectangle(0, 0, 200, 20, fill="#222222", outline="")
        self.fill_bar = self.canvas.create_rectangle(0, 0, 0, 20, fill="#00ff66", outline="")

    def refresh_resource_percentage(self, utilization_pct: float):
        print("\n\033[1;32m--- G.O.D. HARDWARE CONSUMPTION TRACE ---\033[0m")
        # Calculate dynamic horizontal pixel width scaling factor
        pixel_width = int((utilization_pct / 100.0) * 200)
        self.canvas.coords(self.fill_bar, 0, 0, pixel_width, 20)
        
        # Shift bar rendering spectrum if utilization crosses a critical scale
        color = "#00ff66" if utilization_pct < 75.0 else "#ff3333"
        self.canvas.itemconfig(self.fill_bar, fill=color)
        logger.info(f"Resource tracking interface recalculated: {utilization_pct}% allocation profile.")

if __name__ == "__main__":
    root = tk.Tk()
    meter = CanvasResourceMeter(root)
    
    # Simulate an active thread scheduler measurement event
    root.after(100, lambda: meter.refresh_resource_percentage(random.uniform(42.1, 68.9)))
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 116 CANVAS METRIC GAUGES STABLE.\033[0m\n")
