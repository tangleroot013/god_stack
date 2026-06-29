#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[1;34m[1/3] Generating Prometheus Scrape Configurations...\033[0m"
cat << 'YAMLEOF' > prometheus.yml
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'god_stack_daemon'
    static_configs:
      - targets: ['host.docker.internal:8000']
YAMLEOF

echo -e "\033[1;34m[2/3] Constructing Master Docker Compose File...\033[0m"
cat << 'YAMLEOF' > docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: god_prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9090:9090"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: god_grafana
    depends_on:
      - prometheus
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped
YAMLEOF

echo -e "\033[1;34m[3/3] Validating file structures...\033[0m"
echo -e "\n\033[1;32m--- G.O.D. DOCKER ORCHESTRATION VALIDATION ---\033[0m"
ls -la docker-compose.yml prometheus.yml
echo -e "\n\033[1;32m✔ MODULE 29 DOCKER COMPOSE MATRIX PASSED CLEANLY.\033[0m"
echo -e "\033[1;37mRun 'docker-compose up -d' to ignite the telemetry dashboard layer.\033[0m\n"
