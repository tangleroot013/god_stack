#!/usr/bin/env bash
set -euo pipefail

log_info() { echo -e "\033[1;34m$(date +'%H:%M:%S')\033[0m | \033[1;34m[SHIP-INFRA]\033[0m $1"; }
log_error() { echo -e "\033[1;31m$(date +'%H:%M:%S')\033[0m | \033[1;31m[SHIP-FAIL]\033[0m $1" >&2; }

current_branch=$(git branch --show-current)

log_info "Initiating pure-python syntax validation..."
python3 -c '
import sys, py_compile
from pathlib import Path
for f in ["patch_ingest_shedder.py", "patch_raw_shedder.py", "ui/retro_ui.py"]:
    if Path(f).exists():
        py_compile.compile(f, doraise=True)
'

log_info "Pushing validated commits to origin on branch: ${current_branch}"
git push origin "${current_branch}"
