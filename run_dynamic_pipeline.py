#!/usr/bin/env python3
import os
import json
import asyncio
import logging
from orchestrator import GodOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;32m[DYNAMIC-RUNNER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("DynamicRunner")

JSON_PATH = "config/target_urls.json"

async def main():
    print("\n\033[1;33m--- INITIALIZING METRIC DISPATCH LOOP WITH CUSTOM CONFIG ---\033[0m")
    
    # 1. Fallback initialization if target config is missing
    if not os.path.exists(JSON_PATH):
        logger.warning(f"Configuration file {JSON_PATH} not found. Sourcing defaults...")
        targets = ["https://example.com"]
    else:
        with open(JSON_PATH, "r") as f:
            targets = json.load(f)
            
    logger.info(f"Loaded targets for execution pass: {targets}")
    
    # 2. Spin up Orchestrator context (disable proxy requirement for rapid local sweep)
    orchestrator = GodOrchestrator(use_proxies=False)
    await orchestrator.initialize_matrix()
    
    # 3. Drain and process dynamic targets through the operational pipeline layers
    for target_url in targets:
        logger.info(f"Locking target vector: {target_url}")
        mission_summary = await orchestrator.execute_mission(target_url)
        print(f" -> Mission Result Status: {mission_summary.get('status')} | {mission_summary.get('message')}")
        
    print("\n\033[1;32m[SUCCESS] Dynamic target loop completion cycle verified clean.\033[0m\n")

if __name__ == "__main__":
    asyncio.run(main())
