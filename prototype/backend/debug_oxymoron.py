import sys
import os

# Add the current directory to sys.path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), "app"))

from app.pipeline import Pipeline
from app.logic import LogicEngine
from app.models import MeaningGraph

def debug_oxymoron():
    text = "I have to build a tall short building."
    print(f"Processing text: '{text}'")
    
    pipeline = Pipeline()
    # Generate a dummy doc_id
    graph = pipeline.process(text, "debug-doc-id")
    
    print("\n--- Graph Nodes ---")
    for node in graph.nodes:
        print(f"ID: {node.id}, Label: '{node.label}', Type: {node.type}")
        
    print("\n--- Graph Edges ---")
    for edge in graph.edges:
        print(f"Source: {edge.source} -> Target: {edge.target}, Label: '{edge.role}'")
        
    print("\n--- Assertions ---")
    for assertion in graph.assertions:
        print(f"Subject: {assertion.subject}, Predicate: {assertion.predicate}, Object: {assertion.object}")

    print("\n--- Logic Engine Checks ---")
    engine = LogicEngine(graph)
    contradictions = engine.find_contradictions()
    print(f"Contradictions found: {len(contradictions)}")
    for c in contradictions:
        print(f"- {c}")

    print("\n--- Oxymoron Checker ---")
    from app.checkers.oxymoron import OxymoronChecker
    oxy_checker = OxymoronChecker()
    diagnostics = oxy_checker.check(graph)
    print(f"Oxymorons found: {len(diagnostics)}")
    for d in diagnostics:
        print(f"- {d.message}")

if __name__ == "__main__":
    debug_oxymoron()
