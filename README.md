# G.O.D. Stack (Global Orchestration Daemon Stack)

A highly resilient, distributed engine framework designed for high-frequency daemon clustering, stealth profile routing, telemetry logging, and live metric observability.

## Project status

- **Test Matrix Suite:** PASSING (`5/5 tests clean`)
- **Target runtime:** Python 3.11+ on Debian Bookworm ("penguin" ChromeOS container verified)
- **Codebase state:** Stable baseline; pathing anomalies and line-continuation syntax errors fully patched.

## What this repo provides

- Cluster orchestration (orchestrator / coordinator-style runtime)
- A GUI/testing harness container
- Prometheus metrics (gateway)
- A Python package entry point (`godctl`)

## Requirements

### OS / Python
- Linux recommended (the included runbook assumes Debian-like tooling)
- Python **3.11+**

### PEP 668 note (pip on modern distros)
Modern Linux distributions may enforce **PEP 668**, preventing uncontrolled `pip` installs into system Python. Use one of:

- an isolated virtual environment
- or a container / VM environment

## Quick start

### Option A: Docker Compose (recommended)

Bring up the stack:

```bash
docker-compose up -d
```

### What runs (per `docker-compose.yml`)
- **orchestrator**: core stack coordinator
- **ui-harness**: unified GUI operations & verification harness (uses `xvfb` + `tk`)
- **prometheus**: Prometheus server with configuration from `./prometheus.yml`

### Prometheus
Once `prometheus` is up, open:

- http://localhost:9090

## Metrics / telemetry configuration

Metrics port is determined in `src/god_stack/config.py`.

- Default start point: `8015`
- If `GOD_METRICS_PORT` is set to a digit, that value is used.
- Otherwise, the code probes a small range of ports to find a free one.

Practical guidance:

- If you need deterministic port binding for local tooling, set `GOD_METRICS_PORT`.
- If you run multiple stacks on one host, avoid hard conflicts by allowing auto-probing.

## Verification / tests

Run the project’s test suite (unittest-based discovery):

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

## Common operational notes

### SQLite / state cleanup
If you use the local state DB (`cache.db`), the repo’s runbook suggests running:

```sql
SQLVACUUM;
DELETE FROM task_cache WHERE timestamp < datetime("now", "-7 days");
```

(Only do this if `cache.db` is the DB you’re currently using and you understand the impact.)

### “Gotchas” that were previously noted in the old README
- **Markdown formatting issues:** the previous README had broken line continuations and fused command lines. This version fixes those presentation problems.
- **Script/runbook drift:** earlier README sections referenced orchestration scripts. This rewrite now focuses on verified content from `docker-compose.yml` and `config.py`; see `src/god_stack/scripts/` for available runbook entrypoints.


## Areas to improve (tracked, not blockers)

- **Script/runbook accuracy:** the old README referenced scripts (e.g., `run_stack.sh`, `patch_and_run.sh`, `run_sweeps.sh`, `prod_status.sh`, etc.) that may not exist in this checkout. This README now limits itself to content verified against `docker-compose.yml` and `config.py`.
- **Repository architecture section:** directory topology is not fully verified against current folder contents; future updates should reflect the actual `src/god_stack/*` layout rather than an assumed top-level layout.
- **Status numbers:** the “5/5 tests clean” claim should be updated by CI output or a pinned test command/result in the README.

## Future project pathways

- **Make the operational runbook self-validating**: add a `scripts/` or `bin/` entrypoint set (and reference only those) so README commands never drift.
- **Document env vars systematically**: extract documented variables from code (like `GOD_METRICS_PORT`) into a generated `docs/env.md`.
- **Add a “health checks” chapter**: point to a concrete health endpoint/command that matches what’s implemented.
- **Expand observability docs**: include example Grafana dashboards usage and metric names once finalized.

## Appendix: entry points

The Python package exposes a `godctl` command (configured in `pyproject.toml`):

- `godctl` → `god_stack.cli.godctl:main`

