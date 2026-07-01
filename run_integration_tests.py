import asyncio
from frontier_manager import Frontier
from god_scraper import GodScraper
from metrics_exporter import start_metrics_server
from prometheus_client import generate_latest, REGISTRY

async def main():
    print("====================================================")
    print("   RUNNING MULTI-DIMENSIONAL TELEMETRY TEST RUN     ")
    print("====================================================")
    
    try:
        start_metrics_server(port=8000)
        print("[+] Prometheus endpoint live on http://localhost:8000/metrics")
    except Exception as error:
        print(f"[⚠️] Port bind deferred: {error}")
    
    # Hydrate test matrix targets
    for i in range(12):
        Frontier.add_url(f"https://cluster.example.com/api/v1/node_{100 + i}")
    
    Frontier.add_url("https://cluster.example.com/api/v1/node_105")
    Frontier.add_url("https://malformed-debris-string/route")

    scraper = GodScraper()
    await scraper.run()
    
    print("====================================================")
    print(f"RUN SUCCESSFUL: {scraper.processed_count} Target nodes processed safely.")
    print("====================================================")
    
    # Readback registry snapshot to verify labels are formatting correctly for Prometheus
    print("\n[UPGRADED PROMETHEUS METRIC REGISTRY SNAPSHOT]")
    exported_data = generate_latest(REGISTRY).decode("utf-8")
    for line in exported_data.split("\n"):
        if "god_stack_" in line and not line.startswith("#"):
            print(f"  -> {line}")

if __name__ == "__main__":
    asyncio.run(main())
