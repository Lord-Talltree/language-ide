import pytest
from app.pipeline import Pipeline
from app.checkers.continuity import ContinuityChecker
from app.coref import CoreferenceResolver
from app.models import MeaningGraph, Edge, EdgeRole, Provenance

def test_cross_sentence_contradiction():
    """
    Test that the system detects a contradiction between two sentences 
    referring to the same entity via a pronoun.
    
    Sentence 1: "The building is tall."
    Sentence 2: "It is short."
    """
    pipeline = Pipeline()
    
    # Process first sentence
    # "The building is tall" -> Entity(building), Property(tall)
    graph1 = pipeline.process("The building is tall.", "doc1")
    
    # Process second sentence
    # "It is short" -> Entity(it), Property(short)
    graph2 = pipeline.process("It is short.", "doc2")
    
    # Merge graphs manually for the test (simulating SessionManager)
    # In a real session, this happens in session.py
    full_graph = MeaningGraph(
        nodes=graph1.nodes + graph2.nodes,
        edges=graph1.edges + graph2.edges,
        assertions=graph1.assertions + graph2.assertions,
        diagnostics=[],
        provenance=[]
    )
    
    # Run Coreference Resolution
    # This should add a SameAs edge from "It" (doc2) -> "building" (doc1)
    resolver = CoreferenceResolver()
    
    print("\n--- Debugging Nodes ---")
    for n in full_graph.nodes:
        print(f"Node: {n.label} (Type: {n.type}, ID: {n.id})")
    print("-----------------------\n")

    full_graph = resolver.resolve(None, full_graph) # doc argument is unused in current prototype
    
    # Verify SameAs edge exists
    same_as_edges = [e for e in full_graph.edges if e.role == "SameAs"]
    print(f"SameAs Edges found: {len(same_as_edges)}")
    for e in same_as_edges:
        print(f"Edge: {e.source} -> {e.target}")
        
    assert len(same_as_edges) > 0, "Expected CoreferenceResolver to find a link between 'It' and 'building'"
    
    # Run Continuity Checker
    checker = ContinuityChecker()
    errors = checker.check(full_graph)
    
    # Should find 1 error
    assert len(errors) > 0, "Expected ContinuityChecker to find the contradiction"
    
    error = errors[0]
    print(f"Found error: {error.message}")
    
    # Verify error details
    # It should realize "building" is the subject for both
    assert "building" in error.subject or "It" in error.subject
    assert "tall" in error.message
    assert "short" in error.message
