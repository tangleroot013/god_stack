import pytest
import time
from pathlib import Path
from utils.search_ledger import SearchLedger

TMP_VAULT = Path("/tmp/test_timestamp_vault")

@pytest.fixture(autouse=True)
def cleanup_env():
    if TMP_VAULT.exists():
        for f in TMP_VAULT.iterdir(): f.unlink()
        TMP_VAULT.rmdir()
    yield
    if TMP_VAULT.exists():
        for f in TMP_VAULT.iterdir(): f.unlink()
        TMP_VAULT.rmdir()

def test_timestamp_indexing_skips_unchanged():
    ledger = SearchLedger(vault_dir=str(TMP_VAULT))
    TMP_VAULT.mkdir(parents=True, exist_ok=True)
    target_file = TMP_VAULT / "doc1.md"
    target_file.write_text("Telemetry matrix operational data stream.", encoding="utf-8")
    
    # First parsing pass builds standard structural elements
    count_first = ledger.rebuild_index()
    assert (count_first if isinstance(count_first, int) else len(count_first)) == 1
    
    # Reset local transient cache state to confirm disk bypass
    ledger.index_cache.clear()
    
    # Running tracking passes without content modifications must yield a clean bypass
    count_second = ledger.rebuild_index()
    assert (count_second if isinstance(count_second, int) else len(count_second)) == 0
