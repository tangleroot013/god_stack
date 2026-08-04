import tkinter as tk
import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[CLIP-PURGE]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ClipPurge")

class SecureClipboardIngestor:
    def __init__(self, root_window):
        self.root = root_window

    def ingest_and_wipe_clipboard(self) -> str:
        print("\n\033[1;32m--- G.O.D. VOLATILE CLIPBOARD INGESTION MATRIX ---\033[0m")
        try:
            # Safely extract incoming clipboard data structure
            raw_data = self.root.clipboard_get()
            logger.info(f"Successfully fetched copy-paste stream slice ({len(raw_data)} bytes).")
            
            # Instantly flush OS clipboard memory to protect data from adjacent scripts
            self.root.clipboard_clear()
            self.root.clipboard_append("")
            logger.warning("\033[1;33mOS Clipboard wiped. Residual transaction footprints successfully neutralized.\033[0m")
            return raw_data
        except tk.TclError:
            logger.info("Clipboard buffer empty. No data retrieved.")
            return ""

if __name__ == "__main__":
    root = tk.Tk()
    purger = SecureClipboardIngestor(root)
    
    # Seed the mock clipboard with sample data to test the purge cycle
    root.clipboard_clear()
    root.clipboard_append("http://secure-node-target.internal/api/v1")
    
    # Execute the ingest and wipe transaction loop
    purger.ingest_and_wipe_clipboard()
    
    root.after(500, root.destroy)
    root.mainloop()
    print("\n\033[1;32m✔ MODULE 111 CLIPBOARD MEMORY ISOLATION SECURED.\033[0m\n")
