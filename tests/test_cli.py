import pytest
import subprocess
import os

def test_cli_help_flag():
    """Validates that the query script initializes and outputs argument options cleanly."""
    script_path = "/home/tangleroot013/god_stack/bin/query_vault"
    
    assert os.path.exists(script_path), "CLI script asset is missing."
    
    result = subprocess.run(
        [script_path, "-h"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    assert "G.O.D. Stack Markdown Vault Query Utility" in result.stdout
