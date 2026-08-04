import os
import glob
import importlib.util
import logging
from typing import List, Dict, Any
from core.base_extension import BaseExtension

logging.basicConfig(
    level=logging.INFO,
    format="\033[1;35m%(asctime)s\033[0m | \033[1;34m[EXTENSION-LOADER]\033[0m %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ExtensionLoader")

class ExtensionLoader:
    def __init__(self, plugin_dir: str = "parsers"):
        self.plugin_dir = plugin_dir
        self.active_extensions: List[BaseExtension] = []

    async def discover_and_mount(self) -> List[BaseExtension]:
        """Scans the designated extension directory and hot-mounts valid plugins."""
        self.active_extensions.clear()
        search_path = os.path.join(self.plugin_dir, "*_plugin.py")
        plugin_files = glob.glob(search_path)
        
        logger.info(f"Scanning target matrix paths for plug-and-drop extensions inside './{self.plugin_dir}'...")
        
        for file_path in plugin_files:
            module_name = os.path.basename(file_path)[:-3]
            try:
                # Dynamic runtime compilation loop via importlib hooks
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec is None or spec.loader is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Verify and safely extract explicit BaseExtension configurations
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseExtension) and attr != BaseExtension:
                        instance = attr()
                        await instance.initialize()
                        self.active_extensions.append(instance)
                        logger.info(f"Successfully mounted plug-and-drop node: \033[1;32m[{instance.name}]\033[0m")
                        
            except Exception as e:
                logger.error(f"Dynamic compilation failure on extension module {file_path}: {str(e)}")
                
        return self.active_extensions

    async def pipeline_broadcast(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sequentially streams payload contexts across all active plugin instances."""
        current_data = payload
        for ext in self.active_extensions:
            try:
                current_data = await ext.process_payload(current_data)
            except Exception as e:
                logger.error(f"Runtime crash safely caught inside extension engine [{ext.name}]: {str(e)}")
                continue
        return current_data

    async def terminate_extensions(self):
        """Clean teardown context execution loops for all active modules."""
        for ext in self.active_extensions:
            logger.info(f"De-allocating extension subsystem execution frame: [{ext.name}]")
            await ext.teardown()
