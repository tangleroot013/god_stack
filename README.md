# G.O.D. Stack — Global Orchestration Daemon Stack

[![CI](https://github.com/tangleroot013/god_stack/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/tangleroot013/god_stack/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A resilient, distributed engine framework for high-frequency daemon clustering, stealth-profile URL routing, Prometheus telemetry, and live observability via Grafana.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Directory Reference](#directory-reference)
3. [Prerequisites](#prerequisites)
4. [Quick Start](#quick-start)
5. [Configuration](#configuration)
6. [Running the Stack](#running-the-stack)
7. [Observability](#observability)
8. [Testing](#testing)
9. [CI/CD Pipeline](#cicd-pipeline)
10. [Deployment](#deployment)
11. [Known Issues & Gotchas](#known-issues--gotchas)
12. [Contributing](#contributing)

---

## Architecture Overview

```
                        ┌─────────────────────────────────────┐
                        │         god_engine.py               │
                        │   Global execution driver &         │
                        │   multi-node routing supervisor      │
                        └──────────────┬──────────────────────┘
                                       │
               ┌───────────────────────┼──────────────────────┐
               ▼                       ▼                      ▼
   ┌─────────────────┐    ┌─────────────────────┐   ┌──────────────────┐
   │  daemon_core.py │    │  orchestrator.py     │   │  worker_node.py  │
   │  Master loop &  │    │  Task coordinator &  │   │  Compute engine  │
   │  cluster router │    │  scheduling layer    │   │  task consumer   │
   └────────┬────────┘    └──────────┬──────────┘   └────────┬─────────┘
            │                        │                        │
            ▼                        ▼                        ▼
   ┌────────────────┐    ┌───────────────────┐    ┌──────────────────────┐
   │  daemons/      │    │  engines/         │    │  workers/            │
   │  Cluster       │    │  Discrete state   │    │  Local node          │
   │  sub-processes │    │  machines &       │    │  task consumers      │
   └────────────────┘    │  compute layers   │    └──────────────────────┘
                         └───────────────────┘
                                  │
            ┌─────────────────────┼───────────────────────────┐
            ▼                     ▼                           ▼
 ┌──────────────────┐  ┌──────────────────────┐  ┌───────────────────────┐
 │  god_scraper.py  │  │  frontier_manager.py │  │  connection_pool.py   │
 │  Data harvester  │  │  URL frontier queue  │  │  HTTP session pool    │
 │  w/ stealth      │  │  & dedup logic       │  │  & rate limiting      │
 │  profile routing │  └──────────────────────┘  └───────────────────────┘
 └──────────────────┘
            │
 ┌──────────▼──────────────────────────────────────────────────────────┐
 │  Stealth Layer                                                       │
 │  stealth_profiles.yaml / stealth_profiles.json / stealth_mutator.py │
 │  Identity masking, User-Agent rotation, fingerprint management       │
 └──────────────────────────────────────────────────────────────────────┘
            │
 ┌──────────▼──────────────────────────────────────────────────────────┐
 │  Observability Layer                                                  │
 │  utils/prometheus_exporter.py  →  Prometheus  →  Grafana             │
 │  metrics_exporter.py           →  cache.db (SQLite)                  │
 └──────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

1. `god_engine.py` boots the cluster and hands work to `daemon_core.py`.
2. `daemon_core.py` distributes tasks across `daemons/` sub-processes and `worker_node.py` consumers.
3. `god_scraper.py` fetches URLs via `connection_pool.py` using rotating identities from `stealth_profiles.yaml`.
4. `frontier_manager.py` deduplicates and prioritizes the crawl frontier.
5. `url_sanitizer.py` + `courlan_router.py` normalize and validate every URL before it enters the queue.
6. `captcha_handler.py` intercepts challenge pages and routes them to solver backends.
7. `metrics_exporter.py` and `utils/prometheus_exporter.py` emit counters/gauges to Prometheus on `:8000/metrics`.
8. Grafana scrapes Prometheus and renders the operational dashboard.

---

## Directory Reference

```
god_stack/
│
├── .github/
│   └── workflows/
│       └── ci.yml                  ← CI: lint → unit-tests → integration smoke
│
├── api/                            ← Edge command gateways & REST control endpoints
│
├── bin/                            ← Executable entry-point wrappers
│
├── config/                         ← Environment profiles (dev / staging / prod)
│
├── core/                           ← Shared domain primitives used across engines
│
├── cron/                           ← Scheduled task definitions (crontab + Python runners)
│
├── daemons/                        ← Cluster coordinator sub-processes
│
├── engines/                        ← Discrete compute, state machines, task execution
│
├── god_stack/                      ← Python package init & top-level re-exports
│
├── grafana/
│   └── provisioning/
│       └── datasources/            ← Grafana datasource YAML (auto-provisioned)
│
├── migrations/                     ← SQLite schema migrations (numbered, sequential)
│
├── parsers/                        ← Ingestion parsers, scrubbers, validation engines
│
├── schema/                         ← JSON Schema definitions for config & payloads
│
├── scripts/                        ← One-off admin / maintenance scripts
│
├── tests/                          ← pytest test suite
│   ├── test_daemon_cluster.py      ← DaemonCore multi-node clustering tests
│   ├── test_telemetry.py           ← MonitorRelay + WebSocket broadcast tests
│   ├── test_patched_core.py        ← Regression tests for hotfix patches
│   ├── test_production_matrix.py   ← Full production matrix assertions
│   └── test_unified_stack.py       ← End-to-end stack integration tests
│
├── ui/                             ← Web UI assets (status dashboard)
│
├── utils/
│   ├── monitor_relay.py            ← WebSocket broadcast relay for live telemetry
│   └── prometheus_exporter.py      ← Prometheus metrics: Counters, Gauges, Summaries
│
├── vaults/                         ← Encrypted credential containers
│
├── workers/                        ← Task consumers and local node workers
│
│   ── Root-level Python modules ──
│
├── batch_runner.py                 ← Batch job coordinator (parallel task dispatch)
├── captcha_handler.py              ← CAPTCHA detection and solver routing
├── check_health.py                 ← Cluster health probe (use: python check_health.py)
├── connection_pool.py              ← HTTP session pool with rate limiting
├── courlan_router.py               ← URL routing via courlan normalization library
├── daemon_core.py                  ← Master loop & multi-node routing supervisor
├── data_alchemist.py               ← Data transformation and enrichment pipeline
├── data_storage_sync.py            ← cache.db sync and archival coordinator
├── frontier_manager.py             ← Crawl frontier queue with deduplication
├── generate_readme.py              ← Auto-generates README sections from code metadata
├── god_engine.py                   ← Global execution driver (main entry point)
├── god_scraper.py                  ← Data harvester with stealth profile routing
├── matrix_test_runner.py           ← Matrix test dispatcher (runs test permutations)
├── metrics_exporter.py             ← Metrics write path to Prometheus + SQLite
├── orchestrator.py                 ← Task coordinator and scheduling layer
├── provision_farm.py               ← Remote worker provisioning automation
├── run_god_stack.py                ← Primary stack launch script
├── run_unified_stack.py            ← Unified multi-component launcher
├── scavenger.py                    ← Stale record cleanup and cache eviction
├── stealth_mutator.py              ← Runtime stealth profile mutation engine
├── url_sanitizer.py                ← URL normalization, scheme validation, dedup
├── vfs_orchestrator.py             ← Virtual filesystem abstraction layer
├── worker_node.py                  ← Standalone compute engine worker agent
├── worker_simulator.py             ← Load simulator for worker capacity testing
│
│   ── Configuration & Compose ──
│
├── docker-compose.yml              ← Full stack: app + Prometheus + Grafana + node-exporter
├── prometheus.yml                  ← Prometheus scrape config (scrapes :8000/metrics)
├── stealth_profiles.yaml           ← Stealth identity profiles (User-Agents, headers)
├── stealth_profiles.json           ← JSON mirror of stealth profiles (runtime-loaded)
├── requirements.txt                ← Production Python dependencies
├── requirements_core.txt           ← Minimal core dependencies (no optional extras)
├── .env.example                    ← Environment variable template (copy → .env)
│
│   ── Shell Scripts ──
│
├── run_stack.sh                    ← Bring up the full daemon cluster
├── run_orchestrator.sh             ← Start orchestrator in isolation
├── run_orchestrator_clean.sh       ← Orchestrator with clean log state
├── run_sweeps.sh                   ← Performance profiling sweep pipeline
├── prod_orchestrator.sh            ← Production orchestration with log staging
├── prod_status.sh                  ← Live cluster health, node, socket audit
├── release_prod.sh                 ← Sign + export production assets
├── finalize_deployment.sh          ← Final deployment handoff sequence
├── finalize_god_stack.sh           ← Full stack finalization (post-deploy)
├── finalize_release.sh             ← Release artifact finalization
├── deploy_orchestrator.sh          ← Orchestrator deployment
├── deploy_missing_stealth_core.sh  ← Stealth core deployment (missing-module recovery)
├── run_final_unification.sh        ← Final unification run (merge multi-branch state)
├── run_god_stack_patch.sh          ← Apply patches then launch stack
├── patch_and_run.sh                ← Inline hotfix + immediate rerun
├── vault_lock.sh                   ← Lock down credential vaults pre-deploy
├── verify_logs.sh                  ← Log integrity verification
├── verify_stack.py                 ← Stack component verification (Python)
├── verify_stealth_matrix.sh        ← Stealth matrix consistency check
├── phantom_watchdog.sh             ← Watchdog: restarts dead daemon processes
│
│   ── Patch Modules ──
│
├── patch_execution_delay.py        ← Patches scheduler execution delay config
├── patch_ingest_shedder.py         ← Patches ingest load-shedding thresholds
├── patch_mmap_gateway.py           ← Patches mmap gateway alignment
├── patch_pipeline.py               ← Patches pipeline stage wiring
├── patch_raw_shedder.py            ← Patches raw queue shedding policy
├── patch_server.py                 ← Patches server socket configuration
├── patch_worker.py                 ← Patches worker concurrency limits
│
│   ── Systemd ──
│
├── god-orchestrator.service        ← systemd unit for the orchestrator daemon
│
│   ── Artifacts / Backups ──
│
└── sitecustomize.py.bak            ← BACKUP — do not import; network intercept shim
```

---

## Prerequisites

### System packages (recommended for container/VM environments)

```bash
sudo apt update
sudo apt install -y \
    python3.11 \
    python3-pip \
    python3-prometheus-client \
    python3-websockets \
    docker.io \
    docker-compose-plugin
```

### Python virtual environment (recommended for local dev)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **PEP 668 note:** Modern Debian/Ubuntu prevents unmanaged system-wide `pip` installs. Use either `apt` packages (above) or a virtualenv.

### Minimum dependency versions

| Package              | Minimum | Reason                                           |
|----------------------|---------|--------------------------------------------------|
| `websockets`         | 10.0    | `from websockets import ConnectionClosed` export |
| `prometheus_client`  | 0.16.0  | `CollectorRegistry` API stability                |
| `courlan`            | 0.9.0   | `normalize_url` signature                        |
| Python               | 3.11    | `asyncio.TaskGroup`, `tomllib` stdlib            |

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/tangleroot013/god_stack.git
cd god_stack

# 2. Copy environment template
cp .env.example .env
# Edit .env with your settings

# 3. Install dependencies
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. Verify the stack is healthy
python check_health.py

# 5. Launch
./run_stack.sh
```

---

## Configuration

### Environment variables (`.env`)

| Variable                  | Default          | Description                                    |
|---------------------------|------------------|------------------------------------------------|
| `GOD_STACK_ENV`           | `development`    | Runtime environment (`development`/`production`) |
| `MAX_CONCURRENT_WORKERS`  | `2`              | Scale to `8`–`16` for production VMs            |
| `PROMETHEUS_PORT`         | `8000`           | Port for `/metrics` endpoint                   |
| `CACHE_DB_PATH`           | `cache.db`       | SQLite task cache path                         |
| `LOG_DIR`                 | `./logs`         | Operational log output directory               |
| `STEALTH_PROFILE_PATH`    | `stealth_profiles.yaml` | Active stealth profile source           |
| `CAPTCHA_BACKEND`         | `none`           | CAPTCHA solver: `none`, `2captcha`, `local`    |

### Stealth profiles (`stealth_profiles.yaml`)

Each profile entry defines a complete browser fingerprint (User-Agent, Accept headers, TLS fingerprint hints). The `stealth_mutator.py` rotates these at runtime. See `schema/stealth_profile.schema.json` for the full field spec.

---

## Running the Stack

### Full cluster (Docker Compose)

```bash
docker-compose up -d
```

This starts: god_stack app + Prometheus (`:9090`) + Grafana (`:3000`) + node-exporter.

### Local process mode

```bash
# Full daemon cluster
./run_stack.sh

# Orchestrator only
./run_orchestrator.sh

# With clean log state
./run_orchestrator_clean.sh
```

### systemd (production)

```bash
sudo cp god-orchestrator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now god-orchestrator
```

---

## Observability

### Prometheus metrics (`:8000/metrics`)

| Metric Name        | Type    | Component                  | Description                                 |
|--------------------|---------|----------------------------|---------------------------------------------|
| `JOBS_PROCESSED`   | Counter | `worker_node.py`           | Total successfully processed payloads       |
| `ERROR_RATIO`      | Gauge   | `utils/prometheus_exporter.py` | Live error rate; alert threshold: >0.15 |
| `ACTIVE_DAEMONS`   | Gauge   | `daemon_core.py`           | Active sub-node cluster tracking units      |
| `FRONTIER_DEPTH`   | Gauge   | `frontier_manager.py`      | Current crawl frontier queue depth          |
| `STEALTH_ROTATIONS`| Counter | `stealth_mutator.py`       | Cumulative profile rotation events          |

### Grafana dashboard

Navigate to `http://localhost:3000` (default credentials in `.env.example`). The Prometheus datasource is auto-provisioned from `grafana/provisioning/datasources/`.

### Live cluster status

```bash
./prod_status.sh              # node allocation + socket telemetry
python check_health.py        # structured health probe with exit code
```

---

## Testing

```bash
# Full test suite
python -m pytest tests/ -v --tb=short

# With coverage
python -m pytest tests/ --cov=. --cov-report=term-missing

# Single file
python -m pytest tests/test_telemetry.py -v

# Known indentation fix for test_daemon_cluster.py (line 11)
# If you see IndentationError after a patch run:
sed -i '11s/^/    /' tests/test_daemon_cluster.py
```

### Test matrix

| Test file                     | Scope                                              |
|-------------------------------|----------------------------------------------------|
| `test_daemon_cluster.py`      | DaemonCore multi-node clustering and failover      |
| `test_telemetry.py`           | MonitorRelay lifecycle + WebSocket teardown        |
| `test_patched_core.py`        | Regression coverage for all applied hotfixes       |
| `test_production_matrix.py`   | Production-profile permutation assertions          |
| `test_unified_stack.py`       | End-to-end stack boot + task flow integration      |

---

## CI/CD Pipeline

Three sequential jobs run on every push to `main`, `feature/**`, and `hotfix/**`:

```
push / PR
    │
    ▼
[lint]  flake8 + mypy (non-blocking type errors)
    │ pass
    ▼
[unit-tests]  pytest + coverage + websockets version gate
    │ pass
    ▼
[integration]  module import smoke + prometheus smoke + health check smoke
```

All GitHub Actions are pinned to commit SHAs (supply-chain hardening). Coverage XML is uploaded as a build artifact.

---

## Deployment

### Production sequence

```bash
# 1. Lock credential vaults
./vault_lock.sh

# 2. Stage and sign release artifacts
./release_prod.sh

# 3. Deploy orchestrator
./deploy_orchestrator.sh

# 4. Finalize
./finalize_deployment.sh

# 5. Verify
./verify_stack.py
./verify_logs.sh
```

### Database maintenance (`cache.db`)

```sql
-- Compact the database
VACUUM;

-- Evict task records older than 7 days
DELETE FROM task_cache WHERE timestamp < datetime('now', '-7 days');
```

---

## Known Issues & Gotchas

### 1. `IndentationError` in `tests/test_telemetry.py` (FIXED in current HEAD)

**Root cause:** The `from websockets import ConnectionClosed` line was committed with 3 leading spaces, causing a Python parse error before any tests ran. Fixed by removing the indentation.

### 2. `IndentationError` in `tests/test_daemon_cluster.py` after patch runs

`patch_and_run.sh` can strip mock definitions flush to column 0. Fix:

```bash
sed -i '11s/^/    /' tests/test_daemon_cluster.py
```

### 3. `websockets.ConnectionClosed` import path

`ConnectionClosed` is exported from `websockets` top-level since v10.0. If you're on v9.x or below, the import will fail. `requirements.txt` specifies `websockets>=10.0`; CI enforces this with a version gate.

### 4. PEP 668 system-wide pip blocked

Use `apt install python3-<pkg>` or a virtualenv. Do not use `pip install --break-system-packages` in production.

### 5. `sitecustomize.py.bak`

This file is a network intercept shim backup. It must not be named `sitecustomize.py` in any environment where Python starts, or it will execute implicitly at interpreter start and interfere with package imports.

---

## Contributing

1. Branch from `main` using `feature/<scope>-<description>` or `hotfix/<description>`.
2. Run `flake8` and `pytest` locally before pushing.
3. CI must pass all three jobs (lint → unit-tests → integration) before merge.
4. Patch files (`patch_*.py`) should have a corresponding regression test in `test_patched_core.py`.
