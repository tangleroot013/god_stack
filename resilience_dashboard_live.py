#!/usr/bin/env python3
"""
Real-time dashboard that polls /metrics endpoint.
Shows live worker progress, throughput, ETA.
"""
import requests
import time
from datetime import timedelta

def format_progress_bar(processed, total, width=30):
    """Visual progress bar."""
    filled = int((processed / total) * width) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    pct = int((processed / total) * 100) if total > 0 else 0
    return f"[{bar}] {pct}%"

def display_dashboard():
    """Fetch metrics and display live dashboard."""
    try:
        resp = requests.get("http://127.0.0.1:5555/metrics", timeout=2)
        data = resp.json()
    except:
        print("[!] Metrics server not responding. Start metrics_server.py")
        return

    global_stats = data["global"]
    workers = data["workers"]
    elapsed = data["elapsed_seconds"]
    throughput = data["throughput_urls_per_sec"]
    eta = data["eta_seconds"]
    total = data["total_urls"]
    processed = global_stats["processed"]

    print("\n" + "="*70)
    print(" LIVE RESEARCH PIPELINE DASHBOARD ")
    print("="*70)
    print(f"Overall Progress: {format_progress_bar(processed, total)}")
    print(f"Processed: {processed}/{total} | Throughput: {throughput:.2f} URLs/s | ETA: {timedelta(seconds=int(eta))}")
    print("\nWorker Status:")
    for worker_id, stats in sorted(workers.items()):
        worker_processed = stats['processed']
        worker_success = stats['success']
        worker_quarantined = stats['quarantined']
        print(f"  {worker_id}: {worker_processed:3d} processed | {worker_success:3d} success | {worker_quarantined:1d} quarantined")
    print(f"\nElapsed: {timedelta(seconds=int(elapsed))} | Success Rate: {(global_stats['success']/max(processed, 1)*100):.1f}%")
    print("="*70 + "\n")

if __name__ == "__main__":
    while True:
        display_dashboard()
        time.sleep(0.5)  # Refresh every 500ms
