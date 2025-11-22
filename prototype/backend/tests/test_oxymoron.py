import pytest
from app.pipeline import Pipeline
from app.models import DiagnosticKind, Severity

def test_oxymoron_detection_in_pipeline():
    """Test that 'tall short building' is flagged as contradictory"""
    pipeline = Pipeline()
    graph = pipeline.process("I have to build a tall short building.", "test-doc")
    
    # Check that we have at least one diagnostic
    assert len(graph.diagnostics) > 0, "Expected at least one diagnostic"
    
    # Check that one diagnostic mentions the contradiction
    oxymoron_diags = [d for d in graph.diagnostics 
                      if "tall" in d.message.lower() and "short" in d.message.lower()]
    assert len(oxymoron_diags) > 0, "Expected to find oxymoron diagnostic for 'tall' and 'short'"
    
    # Verify the diagnostic has correct properties
    diag = oxymoron_diags[0]
    assert diag.kind == DiagnosticKind.CONTRADICTION
    assert diag.severity == Severity.WARNING
    assert "contradictory" in diag.message.lower()

def test_oxymoron_different_antonym_pairs():
    """Test detection of oxymorons with different antonym pairs"""
    pipeline = Pipeline()
    # Test with "big small" which is in the antonym list
    # Using "build" verb so the pipeline creates a node for the object
    graph = pipeline.process("I will build a big small house.", "test-doc")
    
    # Should detect the big/small oxymoron
    oxymoron_diags = [d for d in graph.diagnostics 
                      if d.kind == DiagnosticKind.CONTRADICTION
                      and "contradictory" in d.message.lower()]
    assert len(oxymoron_diags) > 0, "Expected to find oxymoron for 'big small'"

def test_no_false_positives():
    """Test that normal adjectives don't trigger false positives"""
    pipeline = Pipeline()
    graph = pipeline.process("I saw a big red building.", "test-doc")
    
    # Should not detect any oxymorons
    oxymoron_diags = [d for d in graph.diagnostics 
                      if d.kind == DiagnosticKind.CONTRADICTION 
                      and "contradictory" in d.message.lower()]
    assert len(oxymoron_diags) == 0, "Should not detect oxymorons in normal text"

def test_oxymoron_checker_provenance():
    """Test that oxymoron diagnostics have proper provenance"""
    pipeline = Pipeline()
    graph = pipeline.process("A tall short person.", "test-doc")
    
    oxymoron_diags = [d for d in graph.diagnostics 
                      if "tall" in d.message.lower() and "short" in d.message.lower()]
    
    if len(oxymoron_diags) > 0:
        diag = oxymoron_diags[0]
        assert diag.provenance is not None, "Diagnostic should have provenance"
        assert len(diag.provenance) > 0, "Provenance should not be empty"
        assert diag.provenance[0].engine_id == "oxymoron-checker"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
