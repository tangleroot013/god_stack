import pytest
import asyncio
import json
import shutil
from pathlib import Path
from aiohttp import web, ClientSession
from utils.queue_manager import RedisQueueManager
from api.obsidian_webhook import ObsidianWebhook

TMP_VAULT_DIR = Path("/tmp/god_stack_e2e_vault")

@pytest.fixture(scope="module")
def event_loop():
    """Ensure a single persistent event loop handles all async interactions."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def run_around_tests():
    """Isolate testing vault storage layers completely before execution."""
    if TMP_VAULT_DIR.exists():
        shutil.rmtree(TMP_VAULT_DIR)
    TMP_VAULT_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TMP_VAULT_DIR.exists():
        shutil.rmtree(TMP_VAULT_DIR)

@pytest.mark.asyncio
async def test_end_to_end_pipeline_flow():
    # 1. Initialize our components using temporary path parameters
    broker = RedisQueueManager(host='localhost', port=6379)
    webhook_service = ObsidianWebhook(vault_dir=str(TMP_VAULT_DIR))
    
    # Flush any leftover environment states from test Redis databases
    broker.client.flushdb()

    # 2. Spin up the localized Webhook Server engine on an open test port
    runner = web.AppRunner(webhook_service.app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 9991)
    await site.start()

    try:
        # 3. Simulate Worker parsing extraction by pushing directly to the webhook port
        mock_payload = {
            "filename": "e2e_intel_report.md",
            "content": "# Threat Intelligence Feed\nTarget node footprint mapped cleanly.",
            "scores": {
                "confidence": 0.94,
                "entity_density": 7.2,
                "error_count": 0,
                "parsing_type": "structured"
            }
        }

        async with ClientSession() as session:
            async with session.post("http://127.0.0.1:9991/v2/sync", json=mock_payload) as response:
                assert response.status == 200
                resp_json = await response.json()
                assert resp_json["status"] == "synchronized"
                assert "high-confidence" in resp_json["tags"]

        # 4. Read the processed document back from disk storage to ensure formatting integrity
        target_file = TMP_VAULT_DIR / "e2e_intel_report.md"
        assert target_file.is_file()
        
        file_content = target_file.read_text(encoding="utf-8")
        assert file_content.startswith("---")
        assert 'tags: [' in file_content
        assert '"high-confidence"' in file_content
        assert '"entity-rich"' in file_content
        assert '"type/structured"' in file_content
        assert "Target node footprint mapped cleanly." in file_content

    finally:
        # Guarantee teardown of network ports regardless of execution assertions
        await runner.cleanup()
