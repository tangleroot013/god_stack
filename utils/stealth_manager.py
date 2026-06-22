import logging

log = logging.getLogger("StealthManager")

# JavaScript executed at page initialization before target scripts execute
CANVAS_MUTATOR_JS = """
(() => {
    if (!window.HTMLCanvasElement) return;
    
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

    // Mutate data serialization paths
    HTMLCanvasElement.prototype.toDataURL = function(...args) {
        const ctx = this.getContext('2d');
        if (ctx) {
            try {
                const imgData = originalGetImageData.call(ctx, 0, 0, this.width || 1, this.height || 1);
                // Introduce a tiny, imperceptible modification to the first pixel channel
                imgData.data[0] = (imgData.data[0] + 1) % 256;
                ctx.putImageData(imgData, 0, 0);
            } catch (e) {
                // Handle potential cross-origin taint gracefully
            }
        }
        return originalToDataURL.apply(this, args);
    };
})();
"""

class StealthManager:
    """Orchestrates injection scripts into runtime browser contexts to break tracking telemetry."""
    
    @staticmethod
    def apply_hardware_masks(playwright_page) -> bool:
        """Injects anti-fingerprinting overrides at the document initialization line."""
        try:
            # Bind the mutator to fire before any site assets load
            playwright_page.add_init_script(CANVAS_MUTATOR_JS)
            log.info("🎨 Stealth hardware masks successfully attached to active page.")
            return True
        except Exception as e:
            log.error(f"Failed to append execution hooks: {e}")
            return False
