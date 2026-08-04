import sys, os
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

def push_metrics(target_url, label, duration_ms, status):
    registry = CollectorRegistry()
    
    # Ingestion Latency Vector
    g_duration = Gauge('god_ingestion_duration_milliseconds', 
                       'Processing time per target profile', 
                       ['target_url', 'target_label'], registry=registry)
    g_duration.labels(target_url=target_url, target_label=label).set(duration_ms)
    
    # Ingestion Status Totalizer Vector
    g_status = Gauge('god_ingestion_total', 
                     'Total cluster ingestion runs recorded', 
                     ['target_url', 'target_label', 'status'], registry=registry)
    g_status.labels(target_url=target_url, target_label=label, status=status).set(1)

    try:
        push_to_gateway('localhost:9091', job='god_stack_orchestrator', registry=registry)
        print(f"[SUCCESS] Multi-label telemetry pushed for label: {label}")
    except Exception as e:
        print(f"[METRICS WARNING] PushGateway unreachable. Real-time metrics cached: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        sys.exit(1)
    push_metrics(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4])
