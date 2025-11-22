from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.models import MeaningGraph, Diagnostic, Provenance

class Plugin(ABC):
    def __init__(self, engine_id: str, version: str):
        self.engine_id = engine_id
        self.version = version

    @abstractmethod
    def run(self, graph: MeaningGraph, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Returns a dictionary with:
        - diagnostics: List[Diagnostic]
        - knowledge_validations: List[Any]
        - receipts: List[Any]
        """
        pass

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin):
        self._plugins[plugin.engine_id] = plugin

    def get_plugin(self, engine_id: str) -> Plugin:
        return self._plugins.get(engine_id)

    def list_plugins(self) -> List[Dict[str, str]]:
        return [{"id": p.engine_id, "version": p.version} for p in self._plugins.values()]

# Global registry
registry = PluginRegistry()
