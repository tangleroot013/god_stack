#!/usr/bin/env python3
# ==============================================================================
# retro_ui.py – Clean retro UI without terminal corruption
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
    """IBM punch-card style log line"""
    print(f"{COLORS['info']}| {time.strftime('%H:%M:%S')} | {msg[:60]:<60} |{COLORS['reset']}")

def crt_ticker(msg: str):
    """Simple typewriter effect without destructive ANSI codes"""
    print(f"{COLORS['success']}", end="", flush=True)
    for c in msg:
        print(c, end="", flush=True)
        time.sleep(0.02)  # Typewriter speed
    print(f"{COLORS['reset']}")  # Clean newline

def terminal_bell():
    """Safe terminal bell"""
    print("\a", end="", flush=True)

if __name__ == "__main__":
    punch_card_log("System diagnostics: Absolute stability achieved")
    crt_ticker("🔄 Hibernating... Next chron-cycle in 585s")
    terminal_bell()
