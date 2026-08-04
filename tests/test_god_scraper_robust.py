import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from god_scraper import GodScraper
from metrics_exporter import SYSTEM_METRICS

@pytest.fixture(autouse=True)
def reset_metrics():
    """Resets the shared atomic metric counters before every isolated test execution."""
    for key in SYSTEM_METRICS:
        SYSTEM_METRICS[key] = 0

@pytest.mark.asyncio
async def test_process_target_success_forwarding():
    """Validates that a successful fetch updates telemetry accurately."""
    scraper = GodScraper(concurrency_limit=2)
    scraper.profile_name = "stealth_v2_profile"
    scraper.active = True

    mock_result = {
        "status": "SUCCESS",
        "extracted_data": {
            "links": [
                "https://route1.com",
                "https://route2.com",
            ],
        },
    }

    with patch("god_scraper.GodEngineNode.fetch_and_extract", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_result
        await scraper.process_target("https://target-vector.com")

        mock_fetch.assert_called_once_with("https://target-vector.com", profile="stealth_v2_profile")
        assert SYSTEM_METRICS["god_stack_ingestion_attempts_total"] == 1
        assert SYSTEM_METRICS["god_stack_ingestion_success_total"] == 1

@pytest.mark.asyncio
async def test_process_target_reported_failure():
    """Validates that engine failures do NOT increment success counters and track messages."""
    scraper = GodScraper(concurrency_limit=2)
    scraper.profile_name = "hardened_profile"
    scraper.active = True

    mock_failure = {
        "status": "FAILED",
        "error": "403 Forbidden Cloudflare Intercept",
        "extracted_data": {
            "links": [
                "https://route1.com",
                "https://route2.com",
            ],
        },
    }

    with patch("god_scraper.GodEngineNode.fetch_and_extract", new_callable=AsyncMock) as mock_fetch, \
         patch("god_scraper.logger.warning") as mock_warn:
        mock_fetch.return_value = mock_failure
        await scraper.process_target("https://protected-target.com")

        assert SYSTEM_METRICS["god_stack_ingestion_attempts_total"] == 1
        assert SYSTEM_METRICS["god_stack_ingestion_success_total"] == 0

        mock_warn.assert_called_once()
        log_message = mock_warn.call_args[0][0]
        assert "403 Forbidden Cloudflare Intercept" in log_message

@pytest.mark.asyncio
async def test_process_target_unhandled_exception():
    """Validates that system runtime exceptions are caught safely without breaking engine threads."""
    scraper = GodScraper(concurrency_limit=2)
    scraper.profile_name = "fault_test_profile"
    scraper.active = True

    with patch("god_scraper.GodEngineNode.fetch_and_extract", new_callable=AsyncMock) as mock_fetch, \
         patch("god_scraper.logger.error") as mock_err:
        mock_fetch.side_effect = ConnectionResetError("Connection reset by peer egress agent")
        await scraper.process_target("https://unstable-target.com")

        assert SYSTEM_METRICS["god_stack_ingestion_attempts_total"] == 1
        assert SYSTEM_METRICS["god_stack_ingestion_success_total"] == 0

        mock_err.assert_called_once()
        error_log = mock_err.call_args[0][0]
        assert "Connection reset by peer egress agent" in error_log
