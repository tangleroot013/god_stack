#!/usr/bin/env python3
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# --------------------------------------------------------------------------- #
#    Dependencies
# --------------------------------------------------------------------------- #
try:
    import yaml
except ImportError:
    print("[!] PyYAML missing. Install it with: pip3 install pyyaml")
    sys.exit(1)


# --------------------------------------------------------------------------- #
#    Orchestrator class
# --------------------------------------------------------------------------- #
class GodStackOrchestrator:
    def __init__(self, args):
        # ------------------------------------------------------------------- #
        #    Core paths
        # ------------------------------------------------------------------- #
        self.root_dir = Path(__file__).parent.resolve()
        self.compose_path = self.root_dir / "docker-compose.yml"
        self.prometheus_path = self.root_dir / "prometheus.yml"

        # Grafana provisioning paths
        self.grafana_dir = self.root_dir / "grafana"
        self.datasource_dir = self.grafana_dir / "provisioning" / "datasources"

        # ------------------------------------------------------------------- #
        #    Runtime options
        # ------------------------------------------------------------------- #
        self.network_name = args.network
        self.prom_port = args.prom_port
        self.push_port = args.push_port
        self.add_grafana = args.add_grafana

        # Service identifiers (Single Source of Truth)
        self.pushgateway_service = "god_pushgateway_service"
        self.pushgateway_container = "god_pushgateway"
        self.prometheus_service = "god_prometheus"
        self.prometheus_container = "god_prometheus"
        self.grafana_service = "god_grafana"
        self.grafana_container = "god_grafana"

        # Register graceful shutdown for Ctrl+C
        signal.signal(signal.SIGINT, self.graceful_shutdown)

    # ------------------------------------------------------------------- #
    #    Logging helpers
    # ------------------------------------------------------------------- #
    def log(self, msg: str):
        print(f"\033[1;34m[ORCHESTRATOR]\033[0m {msg}")

    def error(self, msg: str):
        print(f"\033[1;31m[ERROR]\033[0m {msg}", file=sys.stderr)
        sys.exit(1)

    def graceful_shutdown(self, sig, frame):
        """Catches SIGINT (Ctrl+C) and safely spins down the infrastructure."""
        print()
        self.log("Interrupt caught! Executing graceful teardown...")
        subprocess.run(
            ["docker-compose", "down", "--remove-orphans"], 
            capture_output=True, 
            check=False
        )
        self.log("[✓] God Stack safely dismantled. Exiting.")
        sys.exit(0)

    # ------------------------------------------------------------------- #
    #    Docker wrapper utilities
    # ------------------------------------------------------------------- #
    def run_cmd(self, cmd: list, check: bool = True) -> subprocess.CompletedProcess:
        try:
            return subprocess.run(
                cmd, capture_output=True, text=True, check=check
            )
        except subprocess.CalledProcessError as e:
            self.error(f"Command failed: {' '.join(cmd)}\n{e.stderr}")

    def container_running(self, name: str) -> bool:
        out = self.run_cmd(
            ["docker", "ps", "--filter", f"name={name}", "--format", "{{.Name}}"],
            check=False,
        )
        return name in out.stdout.splitlines()

    # ------------------------------------------------------------------- #
    #    Config generation
    # ------------------------------------------------------------------- #
    def _write_prometheus_cfg(self):
        """Write prometheus.yml – targets always scrap internal container ports."""
        cfg = {
            "global": {"scrape_interval": "5s", "evaluation_interval": "5s"},
            "scrape_configs": [
                {
                    "job_name": "god_pushgateway",
                    "honor_labels": True,
                    "static_configs": [
                        {"targets": [f"{self.pushgateway_service}:9091"]}
                    ],
                },
                {
                    "job_name": "god_host_exporter",
                    "static_configs": [{"targets": ["host.docker.internal:9100"]}],
                },
            ],
        }
        with open(self.prometheus_path, "w") as f:
            yaml.safe_dump(cfg, f, default_flow_style=False)

    def _write_grafana_provisioning(self):
        """Create the datasource.yaml that Grafana reads on start."""
        self.log("Generating Grafana datasource provisioning files...")
        self.datasource_dir.mkdir(parents=True, exist_ok=True)

        ds = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "access": "proxy",
                    "url": f"http://{self.prometheus_service}:9090",
                    "isDefault": True,
                    "editable": False,
                }
            ],
        }

        dst = self.datasource_dir / "datasource.yaml"
        with open(dst, "w") as f:
            yaml.safe_dump(ds, f, default_flow_style=False)

        self.log(f"[✓] Grafana datasource written to {dst}")

    def generate_configs(self):
        """Build docker-compose.yml and prometheus.yml from runtime arguments."""
        self.log(
            f"Generating configuration matrices on network '{self.network_name}'..."
        )

        compose = {
            "version": "3.8",
            "networks": {
                self.network_name: {"driver": "bridge", "name": self.network_name}
            },
            "services": {
                self.pushgateway_service: {
                    "image": "prom/pushgateway:v1.10.0",
                    "container_name": self.pushgateway_container,
                    "restart": "unless-stopped",
                    "ports": [f"{self.push_port}:9091"],
                    "networks": [self.network_name],
                },
                self.prometheus_service: {
                    "image": "prom/prometheus:v2.53.0",
                    "container_name": self.prometheus_container,
                    "restart": "unless-stopped",
                    "ports": [f"{self.prom_port}:9090"],
                    "volumes": [
                        f"{self.prometheus_path}:/etc/prometheus/prometheus.yml:ro"
                    ],
                    "extra_hosts": ["host.docker.internal:host-gateway"],
                    "networks": [self.network_name],
                },
            },
        }

        # Optional Grafana block injection
        if self.add_grafana:
            self._write_grafana_provisioning()
            compose["services"][self.grafana_service] = {
                "image": "grafana/grafana:10.4.0",
                "container_name": self.grafana_container,
                "restart": "unless-stopped",
                "ports": ["3000:3000"],
                "environment": {
                    "GF_SECURITY_ADMIN_PASSWORD": "admin",
                    "GF_USERS_DEFAULT_THEME": "light",
                },
                "volumes": [
                    f"{self.grafana_dir}/provisioning:/etc/grafana/provisioning:ro"
                ],
                "depends_on": [self.prometheus_service],
                "networks": [self.network_name],
            }

        # Write generated data maps out to runtime assets
        with open(self.compose_path, "w") as f:
            yaml.safe_dump(compose, f, default_flow_style=False)

        self._write_prometheus_cfg()
        self.log("[✓] All configuration files written to disk.")

    # ------------------------------------------------------------------- #
    #    Deploy / Hot-reload
    # ------------------------------------------------------------------- #
    def deploy_or_reload(self):
        """If Prometheus is running, send SIGHUP; otherwise spin up the stack."""
        if self.container_running(self.prometheus_container):
            self.log("Prometheus already running → sending SIGHUP for hot-reload.")
            self.run_cmd(
                ["docker", "exec", self.prometheus_container, "kill", "-SIGHUP", "1"]
            )
            self.log("[✓] Reload signal sent.")
        else:
            self.log("No existing stack – launching fresh deployment.")
            subprocess.run(
                ["docker-compose", "down", "--remove-orphans"],
                capture_output=True,
                check=False,
            )
            self.run_cmd(["docker-compose", "up", "-d"])

    # ------------------------------------------------------------------- #
    #    Health check
    # ------------------------------------------------------------------- #
    def verify_pipeline_health(self, max_retries: int = 5):
        self.log("Waiting for Prometheus targets to become healthy...")
        for attempt in range(1, max_retries + 1):
            time.sleep(attempt)  # Exponential back-off delay
            resp = self.run_cmd(
                ["curl", "-s", f"http://localhost:{self.prom_port}/api/v1/targets"],
                check=False,
            )
            if not resp.stdout.strip():
                self.log(f"Attempt {attempt}/{max_retries}: No data yet – retrying.")
                continue

            try:
                data = json.loads(resp.stdout)
                active = data.get("data", {}).get("activeTargets", [])
            except json.JSONDecodeError:
                self.log(f"Attempt {attempt}/{max_retries}: Bad JSON – retrying.")
                continue

            if not active:
                self.log(f"Attempt {attempt}/{max_retries}: No active targets – retrying.")
                continue

            if all(t.get("health") == "up" for t in active):
                print("\n--- Current Pipeline Realtime Health Status ---")
                for t in active:
                    print(f"[✓] {t.get('scrapeUrl')} -> Health: {t.get('health')}")
                print("-----------------------------------------------\n")
                self.log("[✓] All targets are up – pipeline operational.")
                return
            else:
                self.log(
                    f"Attempt {attempt}/{max_retries}: Some targets down – retrying."
                )

        self.error(
            "Max retries exhausted. Pipeline health check failed. "
            "Run `docker logs god_prometheus` for details."
        )


# --------------------------------------------------------------------------- #
#    CLI entry point
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="God Stack Orchestrator")
    p.add_argument(
        "--network",
        type=str,
        default="god_network",
        help="Docker bridge network name (default: god_network)",
    )
    p.add_argument(
        "--prom-port",
        type=int,
        default=9090,
        help="Host port for Prometheus (default: 9090)",
    )
    p.add_argument(
        "--push-port",
        type=int,
        default=9091,
        help="Host port for Pushgateway (default: 9091)",
    )
    p.add_argument(
        "--add-grafana",
        action="store_true",
        help="Add Grafana service with auto-provisioned Prometheus datasource",
    )
    args = p.parse_args()

    orch = GodStackOrchestrator(args)
    orch.generate_configs()
    orch.deploy_or_reload()
    orch.verify_pipeline_health()
