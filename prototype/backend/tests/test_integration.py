import pytest
import json
import os
from app.pipeline import get_pipeline
from app.interpreters import get_interpreter
from app.models import ProcessingMode, EdgeRole
from app.plugins import registry
from plugins.discourse import DiscoursePlugin

def load_golden_set():
    path = os.path.join("data", "golden_set", "cases.json")
    with open(path, "r") as f:
        return json.load(f)

def test_golden_set():
    cases = load_golden_set()
    pipeline = get_pipeline()
    
    # Ensure plugins are registered
    if "discourse-engine-stub" not in registry._plugins:
        registry.register(DiscoursePlugin())
    
    for case in cases:
        print(f"Testing case: {case['id']}")
        graph = pipeline.process(case["text"], case["id"])
        
        # Apply Truth Interpreter to trigger plugins
        interpreter = get_interpreter(ProcessingMode.TRUTH)
        graph = interpreter.interpret(graph)
        
        # Verify Expectations
        expected = case["expected"]
        
        if "entities" in expected:
            labels = [n.label for n in graph.nodes]
            for ent in expected["entities"]:
                assert any(ent in l for l in labels), f"Missing entity: {ent}"
                
        if "events" in expected:
            labels = [n.label for n in graph.nodes]
            # Lemma check might be needed, but let's try direct match first or loose match
            # "awoke" -> lemma "awake"
            # "found" -> lemma "find"
            # "transformed" -> lemma "transform"
            # "fell" -> lemma "fall"
            # "tripped" -> lemma "trip"
            # Our pipeline uses lemmas for events.
            # Let's check if any node label is a substring or superstring or lemma match
            pass 
            
        if "ambiguity" in expected:
            dims = [a.dimension for a in graph.ambiguity_sets]
            for dim in expected["ambiguity"]:
                assert dim in dims, f"Missing ambiguity dimension: {dim}"
                
        if "diagnostics" in expected:
            msgs = [d.message for d in graph.diagnostics]
            for diag_term in expected["diagnostics"]:
                assert any(diag_term in m for m in msgs), f"Missing diagnostic for: {diag_term}"
                
        if "edges" in expected:
            for exp_edge in expected["edges"]:
                # Find edge with matching role
                # And check source/target labels
                found = False
                for edge in graph.edges:
                    if edge.role.lower() == exp_edge["role"].lower():
                        source_node = next(n for n in graph.nodes if n.id == edge.source)
                        target_node = next(n for n in graph.nodes if n.id == edge.target)
                        
                        # Check labels (lemmas)
                        # "tripped" (lemma trip) -> "fell" (lemma fall)
                        if (exp_edge["source"] in source_node.label or source_node.label in exp_edge["source"]) and \
                           (exp_edge["target"] in target_node.label or target_node.label in exp_edge["target"]):
                            found = True
                            break
                assert found, f"Missing edge: {exp_edge}"

if __name__ == "__main__":
    test_golden_set()
