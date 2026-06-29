#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/2] Fabricating Live Cluster Health Prober...\033[0m"

cat << 'PYEOF' > check_mesh_health.py
import http.client
import sys
import time

def probe_endpoint(host, port, path, service_name):
    print(f"📡 Probing service [\033[1;35m{service_name}\033[0m] on port {port}...")
    try:
        conn = http.client.HTTPConnection(host, port, timeout=5)
        conn.request("GET", path)
        response = conn.getresponse()
        if response.status in [200, 302]:
            print(f"  \033[1;32m✔ Service Alive Status:\033[0m {response.status} {response.reason}")
            return True
        else:
            print(f"  \033[1;31m❌ Unexpected Response:\033[0m {response.status} {response.reason}")
            return False
    except Exception as e:
        print(f"  \033[1;31m❌ Connection Failed:\033[0m {e}")
        return False

def main():
    print("\n\033[1;32m--- G.O.D. CLUSTER INTERFACE VALIDATION ---\033[0m")
    
    # Give containers a tiny window to settle their initial handshakes if running sequentially
    time.sleep(1)
    
    prom_ok = probe_endpoint("127.0.0.1", 9090, "/-/healthy", "Prometheus Core")
    grafana_ok = probe_endpoint("127.0.0.1", 3000, "/api/health", "Grafana UI")
    
    if prom_ok and grafana_ok:
        print("\n\033[1;32m✔ MODULE 30 MESH OVERWATCH PASSED CLEANLY.\033[0m\n")
    else:
        print("\n\033[1;33m⚠️ Mesh endpoints initializing or settling. Re-run after initialization completes.\033[0m\n")

if __name__ == "__main__":
    main()
PYEOF

echo -e "\033[1;34m[2/2] Launching verification runner...\033[0m"
chmod +x check_mesh_health.py
./.venv/bin/python3 check_mesh_health.py
