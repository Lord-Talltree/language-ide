import pytest
from app.pipeline import Pipeline
from app.models import DiagnosticKind, AmbiguityDimension

def test_ambiguity_detection():
    pipeline = Pipeline("en_core_web_sm")
    text = "Gregor Samsa awoke from uneasy dreams, he found himself transformed in his bed into a gigantic insect."
    doc_id = "kafka_doc"
    
    graph = pipeline.process(text, doc_id)
    
    # Check Vagueness Diagnostic
    vagueness_diags = [d for d in graph.diagnostics if d.kind == DiagnosticKind.VAGUENESS]
    assert len(vagueness_diags) > 0
    assert "uneasy" in vagueness_diags[0].message
    
    # Check Figurative Ambiguity
    fig_ambiguities = [a for a in graph.ambiguity_sets if a.dimension == AmbiguityDimension.AMB_FIG]
    assert len(fig_ambiguities) > 0
    alternatives = fig_ambiguities[0].alternatives
    assert len(alternatives) == 2
    assert any("Literal" in alt.label for alt in alternatives)
    assert any("Figurative" in alt.label for alt in alternatives)

if __name__ == "__main__":
    test_ambiguity_detection()
