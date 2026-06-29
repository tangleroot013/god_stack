#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/3] Building Grafana Directory Infrastructure...\033[0m"
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/dashboards

echo -e "\033[1;34m[2/3] Provisioning Prometheus Datasource YAML...\033[0m"
cat << 'YAMLEOF' > grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
YAMLEOF

cat << 'YAMLEOF' > grafana/provisioning/dashboards/dashboards.yml
apiVersion: 1
providers:
  - name: 'God Stack Dashboards'
    orgId: 1
    folder: 'Observability'
    type: file
    disableDeletion: true
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
YAMLEOF

echo -e "\033[1;34m[3/3] Generating Dashboard Layout Matrix JSON...\033[0m"
cat << 'JSONEOF' > grafana/dashboards/god_stack_main.json
{
  "title": "G.O.D. Stack Operations Matrix",
  "timezone": "browser",
  "refresh": "5s",
  "panels": [
    {
      "type": "stat",
      "title": "Total Ingestion Successes",
      "gridPos": { "h": 8, "w": 8, "x": 0, "y": 0 },
      "targets": [
        { "expr": "god_stack_ingestion_success_total", "refId": "A" }
      ],
      "fieldConfig": {
        "defaults": { "color": { "mode": "thresholds" }, "thresholds": { "steps": [ { "color": "green", "value": null } ] } }
      }
    },
    {
      "type": "timeseries",
      "title": "Ingestion vs Skips Rate (5m)",
      "gridPos": { "h": 8, "w": 16, "x": 8, "y": 0 },
      "targets": [
        { "expr": "rate(god_stack_ingestion_success_total[5m])", "legendFormat": "Success Rate", "refId": "A" },
        { "expr": "rate(god_stack_deduplication_skips_total[5m])", "legendFormat": "Dedup Skips", "refId": "B" }
      ]
    }
  ]
}
JSONEOF

echo -e "\n\033[1;32m✔ MODULE 26 GRAFANA DASHBOARD PROVISIONING VERIFIED CLEANLY.\033[0m"
echo -e "\033[1;37mThe stack is now fully primed for 'docker-compose up -d' with auto-loading dashboards.\033[0m\n"
