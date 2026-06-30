import asyncio
from frontier_manager import Frontier
from god_scraper import GodScraper

async def main():
    print("====================================================")
    print("       RUNNING PIPELINE INTEGRATION RUNTIME         ")
    print("====================================================")
    
    for i in range(12):
        Frontier.add_url(f"https://cluster.example.com/api/v1/node_{100 + i}")
    
    Frontier.add_url("https://cluster.example.com/api/v1/node_105")
    Frontier.add_url("https://malformed-debris-string/route")

    scraper = GodScraper()
    await scraper.run()
    
    print("====================================================")
    print(f"COMPLETE: {scraper.processed_count} Nodes routed into execution channels.")
    print("====================================================")

if __name__ == "__main__":
    asyncio.run(main())
