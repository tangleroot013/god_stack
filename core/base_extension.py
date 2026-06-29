import abc
from typing import Dict, Any

class BaseExtension(abc.ABC):
    """
    Abstract contract for G.O.D. Stack Plug-and-Drop modules.
    Any custom script dropped into processing hotpaths must implement these hooks.
    """
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the unique identification string for the plugin module."""
        pass

    @abc.abstractmethod
    async def initialize(self) -> None:
        """Invoked when the module is dynamically loaded into memory at cluster boot."""
        pass

    @abc.abstractmethod
    async def process_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intercepts raw scraped content arrays prior to persistent archival storage sync.
        
        :param payload: Dict dictionary matching target response matrices
        :return: Enhanced, transformed, or enriched payload tracking dictionary
        """
        pass

    @abc.abstractmethod
    async def teardown(self) -> None:
        """Invoked during graceful system loop termination or component hot-reloads."""
        pass
