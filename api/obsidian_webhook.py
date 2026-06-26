from aiohttp import web
from pathlib import Path
from api.obsidian_graph_decorator import GraphDecorator
from utils.log_rotator import get_logger

log = get_logger("ObsidianWebhook")

class ObsidianWebhook:
    def __init__(self, vault_dir="/home/tangleroot013/god_stack/outputs/vault"):
        self.vault_dir = Path(vault_dir)
        self.decorator = GraphDecorator()
        
        self.app = web.Application()
        self.app.add_routes([web.post('/v2/sync', self.handle_sync_payload)])

    async def handle_sync_payload(self, request):
        """Processes worker completion payload and formats storage frontmatter."""
        try:
            data = await request.json()
            filename = data.get("filename", "unnamed.md")
            scores = data.get("scores", {})
            raw_text = data.get("content", "")

            target_file = self.vault_dir / filename
            target_file.write_text(raw_text, encoding="utf-8")

            # Decorate node and commit variables back to storage array
            tags = self.decorator.decorate(scores)
            self.decorator.inject_frontmatter(target_file, tags)

            return web.json_response({"status": "synchronized", "tags": tags}, status=200)
        except Exception as e:
            log.error(f"Webhook processing fault: {e}")
            return web.json_response({"status": "error", "message": str(e)}, status=500)
