#!/usr/bin/env python3
# ==============================================================================
# retro_ui.py – IBM punch-card logs, CRT tickers, terminal bell
# ==============================================================================
import sys
import time
import random

COLORS = {
    "header": "\033[1;35m",
    "info":   "\033[1;36m",
    "success": "\033[1;32m",
    "warning": "\033[1;33m",
    "error":  "\033[1;31m",
    "reset":  "\033[0m"
}

def punch_card_log(msg: str):
    print(f"{COLORS['info']}| {time.strftime('%H:%M:%S')} | {msg[:60]:<60} |{COLORS['reset']}")

def crt_ticker(msg: str):
    for c in msg:
        print(c, end="", flush=True)
        time.sleep(0.001 * random.uniform(0.8, 1.2))
        if random.random() < 0.05:
            print("\033[2K\r", end="")
            print(f"{COLORS['success']}> {COLORS['reset']}", end="", flush=True)
            time.sleep(0.05)

def terminal_bell():
    print("\a", end="")
    for _ in range(3):
        print("\033[?5h", end="", flush=True)
        time.sleep(0.1)
        print("\033[?5l", end="", flush=True)
        time.sleep(0.1)

if __name__ == "__main__":
    punch_card_log("System diagnostics: Absolute stability achieved")
    crt_ticker("🔄 Hibernating... Next chron-cycle in 585s")
    terminal_bell()
