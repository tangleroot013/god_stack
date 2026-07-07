# ==============================================================================
# STRUCTURED MATRIX WEB INTERFACE (matrix_api.py) - FINAL REALIGNED
# Architecture: Non-blocking FastAPI Interface Layer for Relational Storage
# ==============================================================================
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="God Stack Operations Matrix",
    description="Live engineering monitoring surface for task queues and markdown assets.",
    version="1.0.2"
)

DB_PATH = "matrix_vault.db"

class CrawlTarget(BaseModel):
    url: str

def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Relational vault database file not initialized.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"status": "ONLINE", "engine": "Continuous Daemon Master Process v1.0"}

@app.get("/queue")
def get_current_queue():
    """Retrieves all active task distributions mapping from target_url."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, target_url, status FROM crawl_jobs ORDER BY id DESC LIMIT 50;")
        rows = cursor.fetchall()
        return [{"id": r["id"], "url": r["target_url"], "status": r["status"]} for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/payloads")
def get_scraped_payloads():
    """Exposes harvested payloads along with their data tracking profiles."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, url, page_title, created_at FROM scraped_payloads ORDER BY id DESC;")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/enqueue")
def inject_new_target(target: CrawlTarget):
    """Programmatically seeds a new target vector directly into the active engine stack."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM crawl_jobs WHERE target_url = ?;", (target.url,))
        if cursor.fetchone():
            return {"status": "EXISTS", "message": "Target vector already registered within queue parameters."}
            
        cursor.execute("INSERT INTO crawl_jobs (target_url, status) VALUES (?, 'PENDING');", (target.url,))
        conn.commit()
        return {"status": "SUCCESS", "message": f"Successfully queued target vector: {target.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
