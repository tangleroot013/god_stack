import os
import shutil
import pytest
from utils.obsidian_bridge import ObsidianBridge

TMP_SRC = "/tmp/delta_src"
TMP_DEST = "/tmp/delta_dest"

@pytest.fixture
def setup_delta_vaults():
    for path in [TMP_SRC, TMP_DEST]:
        if os.path.exists(path): shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        
    # Valid high-density file
    with open(os.path.join(TMP_SRC, "high_density.md"), "w") as f:
        f.write("---\ndensity: 0.9\n---\n# Data\nContent here.")

    # Low-density target file to drop
    with open(os.path.join(TMP_SRC, "low_density.md"), "w") as f:
        f.write("---\ndensity: 0.4\n---\n# Noise\nIrrelevant dump.")

    yield TMP_SRC, TMP_DEST

    for path in [TMP_SRC, TMP_DEST]:
        if os.path.exists(path): shutil.rmtree(path)

def test_optimized_sync_logic(setup_delta_vaults):
    src, dest = setup_delta_vaults
    bridge = ObsidianBridge(stack_vault=src, obsidian_vault=dest, min_density=0.8)

    bridge.sync_payloads()

    # Check density filter works
    assert os.path.exists(os.path.join(dest, "high_density.md"))
    assert not os.path.exists(os.path.join(dest, "low_density.md"))
