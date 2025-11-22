from abc import ABC, abstractmethod
from typing import List, Optional, Any
from app.models import MeaningGraph, Diagnostic, DiagnosticKind, Severity, ProcessingMode

class BaseInterpreter(ABC):
    @abstractmethod
    def interpret(self, graph: MeaningGraph) -> MeaningGraph:
        pass

class MapInterpreter(BaseInterpreter):
    """
    Default interpreter. Returns the graph as mapped, with basic diagnostics.
    """
    def interpret(self, graph: MeaningGraph) -> MeaningGraph:
        # Map mode: Contradictions are annotations only.
        # Ensure no diagnostics are marked as ERROR unless system failure.
        for diag in graph.diagnostics:
            if diag.kind == DiagnosticKind.CONTRADICTION:
                diag.severity = Severity.WARNING
        return graph

class FictionInterpreter(BaseInterpreter):
    """
    Downgrades world-model conflicts to narrative annotations.
    """
    def interpret(self, graph: MeaningGraph) -> MeaningGraph:
        # Downgrade specific diagnostics
        for diag in graph.diagnostics:
            if diag.kind == DiagnosticKind.CONTRADICTION:
                diag.severity = Severity.INFO
                diag.message = f"[Narrative] {diag.message}"
        return graph

class TruthInterpreter(BaseInterpreter):
    """
    Runs validation plugins and escalates diagnostics.
    """
    def __init__(self, plugins: List[Any] = []):
        self.plugins = plugins

    def interpret(self, graph: MeaningGraph) -> MeaningGraph:
        # Run plugins from registry
        from app.plugins import registry
        
        # For prototype, just run all registered plugins
        # In reality, we'd select based on config
        for plugin in registry._plugins.values():
            result = plugin.run(graph, context={"doc_id": "unknown"}) # Context needs doc_id
            
            # Merge results
            if "diagnostics" in result:
                graph.diagnostics.extend(result["diagnostics"])
            
            if "graph_updates" in result:
                updates = result["graph_updates"]
                if "edges" in updates:
                    graph.edges.extend(updates["edges"])
                if "nodes" in updates:
                    graph.nodes.extend(updates["nodes"])
            
        return graph

def get_interpreter(mode: ProcessingMode) -> BaseInterpreter:
    if mode == ProcessingMode.FICTION:
        return FictionInterpreter()
    elif mode == ProcessingMode.TRUTH:
        return TruthInterpreter()
    else:
        return MapInterpreter()
