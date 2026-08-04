"""Stunning Octo Funicular adapter for the god_stack repository.

Exports `adapter` which implements a simple run(args) API. The adapter is
conservative by default (dry-run) and can perform a safe command when
invoked with --exec.
"""
from pathlib import Path
import subprocess
from typing import List

REPO_ROOT = Path(__file__).resolve().parent


class GodStackAdapter:
    name = "god_stack"
    description = "Adapter for the god_stack repository to integrate with stunning-octo-funicular"

    def run(self, args: List[str]) -> int:
        if "--exec" in args:
            # Prefer running the repo's tests if present
            if (REPO_ROOT / "tests").exists() or (REPO_ROOT / "pyproject.toml").exists():
                cmd = ["/usr/bin/env", "bash", "-lc", "echo Running god_stack tests; pytest -q || true"]
            else:
                cmd = ["/usr/bin/env", "bash", "-lc", "ls -la"]
            print(f"Running adapter command in {REPO_ROOT}: {' '.join(cmd)}")
            return subprocess.run(cmd, cwd=str(REPO_ROOT)).returncode
        else:
            print(f"[dry-run] would run god_stack adapter against {REPO_ROOT}")
            print("Use --exec to execute a safe example command")
            return 0


adapter = GodStackAdapter()
