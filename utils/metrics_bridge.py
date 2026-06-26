#!/usr/bin/env python3
# ==============================================================================
# utils/metrics_bridge.py – Production File-Backed Telemetry Bridge
# ==============================================================================
import os
import json
import time
import tempfile
import logging

logger = logging.getLogger("TelemetryBridge")

class TelemetryBridge:
    def __init__(self, metrics_dir="metrics"):
        self.metrics_dir = metrics_dir
        # Ensure target workspace exists safely across concurrent workers
        os.makedirs(self.metrics_dir, exist_ok=True)
        self.stats = {}
        self.reset()

    def reset(self):
        """Initializes or clears the live telemetry structural dictionary."""
        self.stats = {
            "tasks_total": 0,
            "tasks_successful": 0,
            "tasks_failed": 0,
            "last_latency_ms": 0.0,
            "avg_latency_ms": 0.0,
            "total_latency_ms": 0.0,
            "last_updated": 0
        }

    def record_job(self, success: bool, duration_ms: float):
        """
        Thread-safe updating logic for recording worker executions.
        
        Args:
            success (bool): Flag indicating if execution was fully unblocked.
            duration_ms (float): High-precision calculation of processing time.
        """
        self.stats["tasks_total"] += 1
        self.stats["last_latency_ms"] = float(duration_ms)
        self.stats["total_latency_ms"] += float(duration_ms)
        
        if success:
            self.stats["tasks_successful"] += 1
        else:
            self.stats["tasks_failed"] += 1
            
        # Avoid division by zero bugs dynamically
        total_tasks = self.stats["tasks_total"]
        self.stats["avg_latency_ms"] = self.stats["total_latency_ms"] / total_tasks if total_tasks > 0 else 0.0
        self.stats["last_updated"] = int(time.time())
        
        self._flush()

    def _flush(self):
        """
        Performs an atomic write via replacement to prevent race conditions 
        where the Prometheus scraper reads a partially written zero-byte file.
        """
        target_path = os.path.join(self.metrics_dir, "pipeline_stats.json")
        try:
            # Write to a temporary file in the same directory first
            with tempfile.NamedTemporaryFile("w", dir=self.metrics_dir, delete=False, suffix=".tmp") as tf:
                json.dump(self.stats, tf, indent=2)
                temp_name = tf.name
            
            # Atomic swap operation (POSIX compliant)
            os.replace(temp_name, target_path)
        except Exception as write_fault:
            logger.error(f"Failed to atomize telemetry serialization frame: {write_fault}")
            if 'temp_name' in locals() and os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except OSError:
                    pass

# Singleton instance ready for system-wide imports
telemetry = TelemetryBridge()
