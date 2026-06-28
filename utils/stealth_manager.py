import random
import logging

log = logging.getLogger("StealthManager")

class StealthManager:
    """Central intelligence layer for identity masks and hardware noise injection."""
    
    def __init__(self):
        self.logger = logging.getLogger("StealthManager")

    def generate_canvas_noise_payload(self) -> str:
        """
        Generates a JS payload to inject randomized noise into Canvas rendering.
        Slightly alters pixel readbacks to unique-ify fingerprint signatures.
        """
        r_offset = random.randint(-5, 5)
        g_offset = random.randint(-5, 5)
        b_offset = random.randint(-5, 5)

        return f"""
        (function() {{
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {{
                const imageData = originalGetImageData.apply(this, arguments);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + {r_offset}));     // Red
                    imageData.data[i + 1] = Math.max(0, Math.min(255, imageData.data[i + 1] + {g_offset})); // Green
                    imageData.data[i + 2] = Math.max(0, Math.min(255, imageData.data[i + 2] + {b_offset})); // Blue
                }}
                return imageData;
            }};
        }})();
        """

    @classmethod
    def apply_hardware_masks(cls, page):
        return True

    def dispatch_identity(self, persistent_id=None) -> dict:
        """Generates a synchronized stealth package complete with hardware noise strings."""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "canvas_noise": self.generate_canvas_noise_payload()
        }
