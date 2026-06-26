#!/usr/bin/env python3
import logging

logger = logging.getLogger("MatrixDaemon")

class HardenedDOMParser:
    @staticmethod
    def extract_metrics_safely(html_tree_node) -> dict:
        """
        Defensively extracts data targets from incoming DOM trees.
        Fails forward gracefully with safe fallbacks on mutation anomalies.
        """
        extracted_data = {
            "title": "Unknown Title",
            "url": "",
            "score": 0
        }
        
        if html_tree_node is None:
            return extracted_data

        # Structural extraction for Core Content Links
        try:
            # Look for typical target containers or plain anchors
            title_element = getattr(html_tree_node, "find", lambda *a, **k: None)(class_="titleline")
            if title_element is None:
                title_element = getattr(html_tree_node, "find", lambda *a, **k: None)("a")
                
            if title_element is not None:
                extracted_data["title"] = title_element.get_text(strip=True)
                extracted_data["url"] = title_element.get("href", "")
        except Exception as e:
            logger.warning(f"⚠️ [PARSER ANOMALY] Handled structural variation on Title: {e}")

        # Structural extraction for Telemetry/Score arrays
        try:
            score_element = getattr(html_tree_node, "find", lambda *a, **k: None)(class_="score")
            if score_element is not None:
                score_text = score_element.get_text(strip=True).replace("points", "").strip()
                extracted_data["score"] = int(score_text)
        except (ValueError, TypeError, AttributeError):
            extracted_data["score"] = 0
        except Exception as e:
            logger.warning(f"⚠️ [PARSER ANOMALY] Handled structural variation on Score: {e}")

        return extracted_data
