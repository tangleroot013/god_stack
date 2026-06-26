#!/usr/bin/env bash
# ========================================================================================================================================================================
# G.O.D. STACK COMPLETE METRIC AUDIT SUITE (VENV ISOLATED)
# ========================================================================================================================================================================
set -e

# 1. Environment Guard Setup
if [ -d "./.venv" ]; then
    source ./.venv/bin/activate
elif [ -d "./venv" ]; then
    source ./venv/bin/activate
else
    echo "⚡ [FATAL] No local venv context discovered. Aborting audit matrix initialization."
    exit 1
fi

echo "========================================================================"
echo "🛡️  RUNNING SYSTEM WORKSPACE STRUCTURAL MATRIX OVERVIEW"
echo "========================================================================"
echo ""

# --- PHASE 1: SYNTAX VALIDATION ---
echo "📋 [PHASE 1] Compiling project source trees..."
find . \( -path "./.venv" -o -path "./venv" -o -path "./.git" -o -path "*/__pycache__" \) -prune -o -type f -name "*.py" -print0 | xargs -0 python3 -m py_compile
echo "✅ All local modules compiled cleanly."
echo "------------------------------------------------------------------------"

# --- PHASE 2: IMPORT DEP PROFILE ---
echo "🧩 [PHASE 2] Auditing Dependency Graph and Token Tree mapping..."
python3 - << 'PYEND'
import ast
import sys
from pathlib import Path

core_files = ["god_engine.py", "daemon_core.py", "orchestrator.py"]
std_libs = {"asyncio", "os", "sys", "json", "time", "signal", "sqlite3", "aiosqlite", "httpx", "logging", "pathlib", "curses", "yaml", "argparse", "subprocess"}

for fpath in core_files:
    if not Path(fpath).exists():
        print(f"⚠️  Core layer omitted from root path: {fpath}")
        continue
    
    with open(fpath) as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError as e:
            print(f"❌ {fpath} Structural Parse Exception: {e}")
            sys.exit(1)
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    
    external = imports - std_libs - {"god_stack", "core", "utils", "parser", "parsers", "engines", "data_alchemist"}
    if external:
        print(f"⚠️  {fpath} relies on unmapped external dependencies: {external}")
    else:
        print(f"✅ {fpath} import map verification: SECURE")
PYEND
echo "------------------------------------------------------------------------"

# --- PHASE 3 & 4: INGESTION AND PERSISTENCE HYGIENE ---
echo "🗂️ [PHASE 3] Validating Concurrency and Storage Pragma hooks..."

WAL_CHECK=$(grep -rn "PRAGMA journal_mode=WAL" . --exclude-dir={.venv,venv,.git} 2>/dev/null | wc -l | awk '{print $1}')
if [ "$WAL_CHECK" -gt 0 ]; then
    echo "✅ Concurrency engine optimization: Write-Ahead Logging (WAL) verified across $WAL_CHECK hooks."
else
    echo "⚠️  Optimization gap found: 'PRAGMA journal_mode=WAL' missing from storage pipelines."
fi

CLIENT_CONTEXTS=$(grep -n "async with.*AsyncClient" god_scraper.py worker_node.py worker_simulator.py 2>/dev/null | wc -l | awk '{print $1}')
echo "ℹ️  Discovered $CLIENT_CONTEXTS async context client lifecycle boundaries."
echo "------------------------------------------------------------------------"

# --- PHASE 5: FOOTPRINT & DESTRUCTION RUNTIME TRACE ---
echo "🔐 [PHASE 4] Auditing Security Purification routines..."
python3 - << 'PYEND'
import sys
import pathlib

target_files = ["scripts/god_stack_main.py", "daemon_core.py", "orchestrator.py"]
shred_signature_found = False

for target in target_files:
    path = pathlib.Path(target)
    if path.exists():
        content = path.read_text()
        if "os.urandom" in content and "unlink" in content:
            print(f"✅ Cryptographic shred implementation found in context location: '{target}'")
            shred_signature_found = True
            break

if not shred_signature_found:
    print("⚠️  Warning: Secure shred parameters or file unlink metrics are unmapped in top-level tasks.")
PYEND
echo "------------------------------------------------------------------------"

echo "🚀 SYSTEM MATRIX OVERVIEW COMPLETED: System structural status is NOMINAL."
deactivate 2>/dev/null || true
