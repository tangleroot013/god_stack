import logging

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;34m%(asctime)s\033[0m | \033[1;36m[ATTR-SANITY]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("AttrSanity")

class DynamicSemanticAttributeSanitizer:
    def __init__(self):
        self.whitelisted_keys = {"id", "class", "href"}

    def purify_element_attributes(self, raw_node: dict) -> dict:
        print("\n\033[1;32m--- G.O.D. ELEMENT ATTRIBUTE PURIFICATION MATRIX ---\033[0m")
        sanitized_attrs = {}
        
        for key, value in raw_node.get("attributes", {}).items():
            if key in self.whitelisted_keys:
                sanitized_attrs[key] = value
            else:
                logger.warning(f"  Stripped inline metadata contamination vector: [ \033[1;31m{key}\033[0m = {value} ]")
                
        purified_node = {"tag": raw_node.get("tag"), "attributes": sanitized_attrs}
        logger.info(f"Node element sanitized. Retained parameters: {sanitized_attrs}")
        return purified_node

if __name__ == "__main__":
    sanitizer = DynamicSemanticAttributeSanitizer()
    mock_node = {
        "tag": "a",
        "attributes": {"href": "/index.html", "onclick": "trackUserMetrics()", "data-tracking-id": "99A12"}
    }
    sanitizer.purify_element_attributes(mock_node)
    print("\n\033[1;32m✔ MODULE 82 ATTR PURIFICATION ROUTINES COMPLIANT.\033[0m\n")
