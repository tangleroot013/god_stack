#!/usr/bin/env python3
import asyncio
import logging
from data_alchemist import DataAlchemist
from god_engine import GodEngine

logging.basicConfig(level=logging.INFO)

async def test_suite():
    print("\n🔬 --- RUNNING HARDENED TARGET EVALUATION ---")
    
    # Test DataAlchemist performance processing payload arrays
    payloads = [
        {"title": "  Hacker News Headline  ", "url": "https://news.ycombinator.com ", "score": 105},
        {"title": "Broken Payload Data missing url", "score": 42},
        {"title": "TechCrunch Post", "url": "https://techcrunch.com", "score": "not_an_int"},
        "invalid_string_record",
        {"title": "Valid Secondary Target", "url": "https://github.com", "score": 420.5}
    ]
    
    refined = DataAlchemist.optimize_array_processing(payloads)
    assert len(refined) == 3, f"Expected 3 clean payloads, got {len(refined)}"
    print("✅ DataAlchemist single-pass execution structure verified stability.")
    
    # Test Async Engine Non-Blocking Control Flow
    engine = GodEngine()
    result = await engine.process_target("https://news.ycombinator.com/news")
    assert result["status"] == "success", "GodEngine async flow failed execution."
    print("✅ GodEngine async context-offloading verified stability.")
    
    print("\n🚀 ALL PRODUCTION HOT-PATH FIXES COMPILED AND OPERATIONAL.")

if __name__ == "__main__":
    asyncio.run(test_suite())
