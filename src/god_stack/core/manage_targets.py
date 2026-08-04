#!/usr/bin/env python3
import os
import sys
import json
import sqlite3

JSON_PATH = "config/target_urls.json"
DB_PATH = "god_stack_vfs.db"

def load_json_targets():
    if not os.path.exists(JSON_PATH):
        return []
    with open(JSON_PATH, "r") as f:
        return json.load(f)

def save_json_targets(targets):
    with open(JSON_PATH, "w") as f:
        json.dump(targets, f, indent=4)

def update_db_frontier(url, action="ADD"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS frontier_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            status TEXT DEFAULT 'PENDING',
            depth INTEGER DEFAULT 0
        )
    """)
    if action == "ADD":
        try:
            cursor.execute("INSERT OR IGNORE INTO frontier_queue (url, status, depth) VALUES (?, 'PENDING', 0)", (url,))
            print(f" [VFS] Enqueued target inside SQLite: {url}")
        except Exception as e:
            print(f" [VFS Error] Could not enqueue inside SQLite: {e}")
    elif action == "REMOVE":
        cursor.execute("DELETE FROM frontier_queue WHERE url = ?", (url,))
        print(f" [VFS] Evicted target from SQLite: {url}")
    conn.commit()
    conn.close()

def add_target(url):
    targets = load_json_targets()
    if url in targets:
        print(f" [*] Website '{url}' is already registered.")
        return
    targets.append(url)
    save_json_targets(targets)
    update_db_frontier(url, "ADD")
    print(f" [SUCCESS] Added target source: {url}")

def remove_target(url):
    targets = load_json_targets()
    if url not in targets:
        print(f" [-] Website '{url}' not found in configuration manifest.")
        return
    targets.remove(url)
    save_json_targets(targets)
    update_db_frontier(url, "REMOVE")
    print(f" [SUCCESS] Removed target source: {url}")

def list_targets():
    targets = load_json_targets()
    print("\n--- Current Pipeline Targets ---")
    for idx, url in enumerate(targets, 1):
        print(f"  {idx}. {url}")
    print("--------------------------------\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 manage_targets.py [list | add <url> | remove <url>]")
        sys.argv = ["manage_targets.py", "list"] # Fallback to listing

    action = sys.argv[1].lower()
    if action == "list":
        list_targets()
    elif action == "add" and len(sys.argv) > 2:
        add_target(sys.argv[2])
    elif action == "remove" and len(sys.argv) > 2:
        remove_target(sys.argv[2])
    else:
        print("Invalid operational command mapping.")
