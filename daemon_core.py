#!/usr/bin/env python3
# ==============================================================================
# G.O.D. STACK V2.0.0 ACADEMIC RESEARCH LOCKDOWN INTERACTIVE DAEMON CONTROL
# ==============================================================================
import os
import sys
import time
import asyncio
import logging
import curses
import subprocess
import shutil
from logging.handlers import RotatingFileHandler
from typing import Dict, Any, List

# Ensure isolated logging environment paths exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "daemon_orchestrator.log")

# Setup clean file logging for real-time internal capture streaming
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=1)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

logger = logging.getLogger("LockdownDaemon")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

class AcademicDaemonOrchestrator:
    def __init__(self, interval_seconds: int = 300):
        self.interval = interval_seconds
        self.cycle_count = 0
        self.failures_encountered = 0
        self.last_status = "INITIALIZING CORE SUBPROCESS"
        self.running = True
        self.log_lines: List[str] = []

    def load_latest_logs(self) -> List[str]:
        """Pulls raw execution logs securely from disk buffer for human display mapping."""
        if not os.path.exists(LOG_FILE):
            return ["Waiting for log synchronization stream initialization..."]
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return f.readlines()[-30:]  # Keep last 30 log lines in screen layout
        except Exception:
            return ["Error tracking log transaction pointers."]

    async def run_pipeline(self):
        """Dispatches automated worker cycles inside the isolated python venv."""
        while self.running:
            self.cycle_count += 1
            logger.info(f"Executing Academic Analysis Cycle #{self.cycle_count}")
            self.last_status = f"RUNNING SWEEP NETWORK MATRICES (#{self.cycle_count})"
            
            try:
                process = await asyncio.create_subprocess_exec(
                    "./.venv/bin/python3", "run_all.py",
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    self.last_status = "HOLDING - NOMINAL EXTRATION NOMINAL"
                    logger.info(f"Cycle #{self.cycle_count} tracking sequence processed successfully.")
                else:
                    self.failures_encountered += 1
                    self.last_status = f"EXCEPTION DETECTED (CODE {process.returncode})"
                    logger.error(f"Core execution engine returned non-zero error: {stderr.decode().strip()}")
            except Exception as e:
                self.failures_encountered += 1
                self.last_status = "SUBPROCESS FAULT"
                logger.critical(f"Failed to cleanly reference orchestration thread: {str(e)}")

            # Countdown interval tracking logic
            for remaining in range(self.interval, 0, -1):
                if not self.running:
                    break
                if "HOLDING" in self.last_status or "INITIALIZING" in self.last_status:
                    self.last_status = f"HOLDING - INTERVAL REFRESH IN {remaining}s"
                await asyncio.sleep(1)

    def purge_sensitive_footprint(self):
        """Enforces absolute lockdown compliance by vaporizing volatile tracking objects on disk."""
        logger.handlers.clear()
        file_handler.close()
        
        # Immediate disk scrub sequence across log directories
        if os.path.exists(LOG_DIR):
            shutil.rmtree(LOG_DIR)
        
        # Explicit terminal cleanup feedback
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[1;31m================================================================================")
        print("  [!] LOCKDOWN SECURE PURGE: ACADEMIC SESSION TRACES DELETED SUCCESSFULLY")
        print("================================================================================")
        print("\033[1;32m  -> Directory target path wiped cleanly: ./logs/*")
        print("  -> Session footprint index state: [0 RECORDS REMAINING] Volatile environment safe.\033[0m\n")

    def draw_dashboard(self, stdscr):
        # Configure non-blocking key reads inside curses frame window
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)
        
        # Initialize basic terminal color pairing sets
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        async def ui_loop():
            pipeline_task = asyncio.create_task(self.run_pipeline())
            
            while self.running:
                # Capture escape or system abort keystroke commands (q to exit)
                try:
                    key = stdscr.getch()
                    if key == ord('q') or key == ord('Q'):
                        self.running = False
                        pipeline_task.cancel()
                        break
                except Exception:
                    pass

                stdscr.erase()
                h, w = stdscr.getmaxyx()
                
                # Render System Header Anchors
                stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                stdscr.addstr(0, 0, "=" * (w - 1))
                stdscr.addstr(1, 2, f"G.O.D. STACK v2.0.0  |  ACADEMIC RESEARCH PLATFORM PANEL (PID: {os.getpid()})")
                stdscr.addstr(2, 2, "SECURITY ENVIRONMENT MODE: [ STRICT LOCKDOWN ON SHUTDOWN ]")
                stdscr.addstr(3, 0, "=" * (w - 1))
                stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)

                # Render Main Execution Metrics Matrices
                stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                stdscr.addstr(5, 2, "[+ STATUS MONITOR MATRIX]")
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
                
                stdscr.addstr(6, 4, f"• System State Loop    : {self.last_status}")
                stdscr.addstr(7, 4, f"• Sweep Cycles Run    : {self.cycle_count}")
                stdscr.addstr(8, 4, f"• Subprocess Crashes   : {self.failures_encountered}")
                
                # Render Stream Log Captures Pane Segment
                stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(10, 2, "[+ HUMANISED LIVE SUBPROCESS TRACKING STREAMS]")
                stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
                
                # Render line tracking limits within window geometry rules
                self.log_lines = self.load_latest_logs()
                log_start_row = 11
                max_log_rows = h - log_start_row - 3
                
                for idx, line in enumerate(self.log_lines[-max_log_rows:]):
                    clean_line = line.strip()
                    if len(clean_line) > w - 6:
                        clean_line = clean_line[:w - 9] + "..."
                    stdscr.addstr(log_start_row + idx, 4, f"› {clean_line}")

                # Render System Control Footer Indicators
                stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                stdscr.addstr(h - 2, 2, "[ Press 'q' to break execution thread, initiate lockdown scrub sequence ]")
                stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

                stdscr.refresh()
                await asyncio.sleep(0.5)

        asyncio.run(ui_loop())

def launch_daemon(stdscr):
    orchestrator = AcademicDaemonOrchestrator(interval_seconds=300)
    try:
        orchestrator.draw_dashboard(stdscr)
    finally:
        # Enforce file-shred automation on environment unload
        orchestrator.purge_sensitive_footprint()

if __name__ == "__main__":
    # Wrap system display descriptors cleanly using curses runtime mapping hooks
    curses.wrapper(launch_daemon)
