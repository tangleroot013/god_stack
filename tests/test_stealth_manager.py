import pytest
from unittest.mock import MagicMock
from utils.stealth_manager import StealthManager

def test_stealth_manager_injection_flow():
    mock_page = MagicMock()
    mock_page.add_init_script = MagicMock()
    
    status = StealthManager.apply_hardware_masks(mock_page)
    
    assert status is True
    mock_page.add_init_script.assert_called_once()
