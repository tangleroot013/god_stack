import pytest
import os
import shutil
from utils.obsidian_bridge import ObsidianBridge

TMP_SRC = "/tmp/stack_vault_src"
TMP_DEST = "/tmp/obsidian_vault_dest"

@pytest.fixture
def setup_vault_sandboxes():
    for path in [TMP_SRC, TMP_DEST]:
        if os.path.exists(path): shutil.rmtree(path)
        os.makedirs(path, exist_ok=True)
        
    with open(os.path.join(TMP_SRC, "intel_node_beta.md"), "w") as f:
        f.write("# Threat Intel Profile\nTarget: Matrix Engine Vector")

    yield TMP_SRC, TMP_DEST

    for path in [TMP_SRC, TMP_DEST]:
        if os.path.exists(path): shutil.rmtree(path)

def test_bridge_mirror_and_moc_generation(setup_vault_sandboxes):
    src, dest = setup_vault_sandboxes
    bridge = ObsidianBridge(stack_vault=src, obsidian_vault=dest)
    
    bridge.sync_payloads()
    assert os.path.exists(os.path.join(dest, "intel_node_beta.md"))
    
    mock_results = [{"path": os.path.join(src, "intel_node_beta.md")}]
    bridge.create_moc(mock_results, moc_name="Main_MOC")
    
    moc_file_path = os.path.join(dest, "Main_MOC.md")
    assert os.path.exists(moc_file_path)
    
    with open(moc_file_path, "r") as f:
        content = f.read()
    assert "- [[intel_node_beta]]" in content
