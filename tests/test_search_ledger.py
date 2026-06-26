import pytest
import os
import shutil
from utils.search_ledger import SearchLedger

TMP_VAULT = "/tmp/god_vault"

@pytest.fixture
def setup_mock_vault():
    if os.path.exists(TMP_VAULT): shutil.rmtree(TMP_VAULT)
    os.makedirs(TMP_VAULT, exist_ok=True)
    
    # Generate mock intel captures
    with open(os.path.join(TMP_VAULT, "node_01.md"), "w") as f:
        f.write("# Target Node 01 Info\nStatus: Restricted\nKeyToken: alpha_secure_99")
        
    with open(os.path.join(TMP_VAULT, "node_02.md"), "w") as f:
        f.write("# Target Node 02 Info\nStatus: Open\nMetadata: cleartext")

    yield TMP_VAULT
    if os.path.exists(TMP_VAULT): shutil.rmtree(TMP_VAULT)

def test_ledger_indexing_and_querying(setup_mock_vault):
    ledger = SearchLedger(vault_dir=setup_mock_vault)
    indexed_count = ledger.rebuild_index()
    
    assert indexed_count == 2
    
    # Exact Match Lookup Test
    keyword_hits = ledger.query("Restricted")
    assert len(keyword_hits) == 1
    assert "node_01.md" in keyword_hits[0]["path"]
    
    # Regex Core Pattern Match Test
    regex_hits = ledger.query(r"alpha_\w+_\d+", is_regex=True)
    assert len(regex_hits) == 1
    assert regex_hits[0]["matches_count"] == 1
