import re
import html

class GodDOMParser:
    @staticmethod
    def extract_clean_text(raw_html: str) -> str:
        """Return plain-text content from an HTML fragment."""
        if not raw_html:
            return ""

        # 1. Remove <script> and <style> blocks (including their bodies)
        clean = re.sub(
            r'<script\b[^>]*>.*?</script>',
            ' ',
            raw_html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        clean = re.sub(
            r'<style\b[^>]*>.*?</style>',
            ' ',
            clean,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # 2. Strip HTML comments
        clean = re.sub(r'', ' ', clean, flags=re.DOTALL)

        # 3. Remove any remaining tags, leaving only the text nodes
        clean = re.sub(r'<[^>]+>', ' ', clean)

        # 4. Decode HTML entities (e.g. &#x27; -> ', &amp; -> &)
        clean = html.unescape(clean)

        # 5. Collapse whitespace (tabs, new-lines, multiple spaces) into a single space
        clean = re.sub(r'\s+', ' ', clean).strip()

        return clean

if __name__ == "__main__":
    print("🔬 Testing text extraction layout frame...")
    sample = (
        "<html><head><style>body { color: #fff; }</style></head>"
        "<body><h1>Hacker News</h1>"
        "<script>console.log('test')</script>"
        "<p>Jerry&#x27;s Map is live &amp; processing.</p>"
        "</body></html>"
    )
    parsed = GodDOMParser.extract_clean_text(sample)
    print(f"Parsed Yield: {parsed}")
