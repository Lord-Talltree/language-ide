import pytest
from app.models import MeaningGraph, Node, Edge, NodeType, EdgeRole, ProcessingMode, DiagnosticKind
from app.interpreters import get_interpreter
from app.plugins import registry
from plugins.truth_checker import TruthCheckerPlugin

def test_truth_plugin():
    # Ensure plugin is registered
    if "truth-checker-stub" not in registry._plugins:
        registry.register(TruthCheckerPlugin())

    # Construct a graph with the target pattern
    # Event: transformed -> Theme: insect
    nodes = [
        Node(id="evt_1", type=NodeType.EVENT, label="transformed"),
        Node(id="ent_1", type=NodeType.ENTITY, label="insect")
    ]
    edges = [
        Edge(source="evt_1", target="ent_1", role=EdgeRole.THEME) # Using Theme for now as per plugin logic
    ]
    
    graph = MeaningGraph(
        nodes=nodes,
        edges=edges,
        ambiguity_sets=[],
        context_frames=[],
        diagnostics=[],
        provenance=[]
    )
    
    # Run TruthInterpreter
    interpreter = get_interpreter(ProcessingMode.TRUTH)
    result_graph = interpreter.interpret(graph)
    
    # Check for KnowledgeGap diagnostic
    diags = [d for d in result_graph.diagnostics if d.kind == DiagnosticKind.KNOWLEDGE_GAP]
    assert len(diags) > 0
    assert "Humans cannot biologically transform" in diags[0].message

if __name__ == "__main__":
    test_truth_plugin()
