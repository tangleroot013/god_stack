import pytest
import os
from pathlib import Path
from utils.search_ledger import SearchLedger

TMP_VAULT = Path("/tmp/test_god_vault")

@pytest.fixture(autouse=True)
def run_around_tests():
    if TMP_VAULT.exists():
        for f in TMP_VAULT.iterdir(): f.unlink()
        TMP_VAULT.rmdir()
    if SearchLedger.METADATA_FILE.exists():
        SearchLedger.METADATA_FILE.unlink()
    yield
    if TMP_VAULT.exists():
        for f in TMP_VAULT.iterdir(): f.unlink()
        TMP_VAULT.rmdir()
    if SearchLedger.METADATA_FILE.exists():
        SearchLedger.METADATA_FILE.unlink()

def test_incremental_short_circuit_behavior():
    ledger = SearchLedger(vault_dir=str(TMP_VAULT))
    test_file = TMP_VAULT / "intel_report.md"
    test_file.write_text("Operation Tangleroot core collection sequence active.", encoding="utf-8")

    # Initial capture pass must process data contents
    first_run = ledger.index_file(test_file)
    assert first_run is True
    assert str(test_file) in ledger.index

    # Consecutive iterations without changes must skip heavy parsing work
    second_run = ledger.index_file(test_file)
    assert second_run is False

    # Modifying internal state metrics must drop short-circuits and trigger updates
    test_file.write_text("Operation Tangleroot database tracking modified.", encoding="utf-8")
    third_run = ledger.index_file(test_file)
    assert third_run is True
