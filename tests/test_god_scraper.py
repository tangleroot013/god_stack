import pytest
from unittest.mock import AsyncMock, MagicMock
from god_scraper import GodScraper

@pytest.mark.asyncio
async def test_scraper_fallback_profile():
    """Confirms that GodScraper instantiates and uses internal stealth infrastructure smoothly."""
    scraper = GodScraper()
    assert scraper.identity_handler is not None

@pytest.mark.asyncio
async def test_mocked_scrape_sequence():
    """Validates full parsing orchestration using correctly wired async method mocks."""
    scraper = GodScraper()
    scraper.context = MagicMock()
    
    # Bind new_page as an AsyncMock so it can be directly awaited
    mock_page = AsyncMock()
    scraper.context.new_page = AsyncMock(return_value=mock_page)
    
    mock_page.content.return_value = "<html><body><h1>Scraped!</h1></body></html>"
    mock_page.title.return_value = "Mock Target"
    
    result = await scraper.scrape("https://mock-target.internal", [{"action": "scroll"}])
    assert result["status"] == "success"
    assert "markdown" in result
    assert "Scraped!" in result["markdown"]
