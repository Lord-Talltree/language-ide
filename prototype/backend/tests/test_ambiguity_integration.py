import pytest
from app.pipeline import Pipeline
from app.models import DiagnosticKind

def test_ambiguity_integration():
    """Test that vague terms are flagged by the pipeline integration."""
    pipeline = Pipeline()
    
    # Test case 1: Vague pronoun "it" without antecedent
    # Note: In a single sentence "It is broken", "it" is ambiguous.
    text = "It is broken."
    graph = pipeline.process(text, "test-doc-ambiguity")
    
    # Check for Ambiguity diagnostics
    ambiguity_diags = [d for d in graph.diagnostics if d.kind == DiagnosticKind.AMBIGUITY]
    
    assert len(ambiguity_diags) > 0, "Expected at least one ambiguity diagnostic"
    assert any("it" in d.message.lower() for d in ambiguity_diags), "Expected diagnostic about 'it'"

def test_vague_noun_integration():
    """Test that vague nouns are flagged."""
    pipeline = Pipeline()
    
    text = "Check the file."
    graph = pipeline.process(text, "test-doc-noun")
    
    ambiguity_diags = [d for d in graph.diagnostics if d.kind == DiagnosticKind.AMBIGUITY]
    
    assert len(ambiguity_diags) > 0
    assert any("file" in d.message.lower() for d in ambiguity_diags)
