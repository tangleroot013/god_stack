import pytest
from pathlib import Path
from api.obsidian_graph_decorator import GraphDecorator

TMP_VAULT = Path("/tmp/test_decorator_vault")

@pytest.fixture(autouse=True)
def cleanup_env():
    TMP_VAULT.mkdir(parents=True, exist_ok=True)
    yield
    for f in TMP_VAULT.iterdir(): f.unlink()
    TMP_VAULT.rmdir()

def test_heuristic_tag_assignment():
    decorator = GraphDecorator()
    high_quality_scores = {
        "confidence": 0.95,
        "entity_density": 6.8,
        "error_count": 0,
        "parsing_type": "structured"
    }
    
    tags = decorator.decorate(high_quality_scores)
    assert "high-confidence" in tags
    assert "entity-rich" in tags
    assert "type/structured" in tags
    assert "needs-review" not in tags

def test_frontmatter_disk_injection():
    decorator = GraphDecorator()
    target_file = TMP_VAULT / "node.md"
    target_file.write_text("Raw structural body text.", encoding="utf-8")

    decorator.inject_frontmatter(target_file, ["test-tag"])
    
    updated_content = target_file.read_text(encoding="utf-8")
    assert updated_content.startswith("---")
    assert 'tags: ["test-tag"]' in updated_content
