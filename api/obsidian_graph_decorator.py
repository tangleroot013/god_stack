import logging
from pathlib import Path
from typing import Dict, List

log = logging.getLogger("GraphDecorator")

class GraphDecorator:
    """Auto-tags knowledge graph nodes based on Heuristic Parser Matrix scores."""
    
    SCORE_THRESHOLDS = {
        "high_confidence": 0.85,
        "medium_confidence": 0.60,
        "entity_dense": 5.0,  # Entities detected per sample block
    }

    def decorate(self, scores: Dict[str, any]) -> List[str]:
        """Maps quantitative metadata scores to human-readable Obsidian tags."""
        tags = ["god-stack"]
        
        confidence = scores.get("confidence", 0.0)
        if confidence >= self.SCORE_THRESHOLDS["high_confidence"]:
            tags.append("high-confidence")
        elif confidence >= self.SCORE_THRESHOLDS["medium_confidence"]:
            tags.append("medium-confidence")
        else:
            tags.append("low-confidence")

        if scores.get("entity_density", 0.0) >= self.SCORE_THRESHOLDS["entity_dense"]:
            tags.append("entity-rich")

        if scores.get("error_count", 0) > 0:
            tags.append("needs-review")

        parsing_type = scores.get("parsing_type", "raw")
        tags.append(f"type/{parsing_type}")

        return tags

    def inject_frontmatter(self, file_path: Path, tags: List[str]) -> bool:
        """Injects clean YAML frontmatter arrays into a markdown target file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False

            content = file_path.read_text(encoding="utf-8")
            formatted_tags = ", ".join([f'"{tag}"' for tag in tags])
            frontmatter = f"---\ntags: [{formatted_tags}]\n---\n"

            # Avoid double frontmatter injection
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    # Strip away existing frontmatter block if present
                    content = parts[2].lstrip()

            file_path.write_text(frontmatter + content, encoding="utf-8")
            log.info(f"✅ Enhanced document properties at: {file_path.name}")
            return True
        except Exception as e:
            log.error(f"Failed to inject frontmatter properties: {e}")
            return False
