import pytest
from app.pipeline import Pipeline

def test_modality_extraction():
    """Test that 'might', 'can', 'must' set the modality property."""
    pipeline = Pipeline()
    
    # Test Possibility
    text = "I might build the app."
    graph = pipeline.process(text, "test-doc-modality-1")
    
    # Find the event "build"
    build_node = next((n for n in graph.nodes if "build" in n.label), None)
    assert build_node is not None
    assert build_node.properties.get("modality") == "possible"

    # Test Necessity
    text_must = "I must finish this."
    graph_must = pipeline.process(text_must, "test-doc-modality-2")
    finish_node = next((n for n in graph_must.nodes if "finish" in n.label), None)
    assert finish_node is not None
    assert finish_node.properties.get("modality") == "necessary"

def test_negation_extraction():
    """Test that 'not' sets the polarity property."""
    pipeline = Pipeline()
    
    text = "I did not go to the store."
    graph = pipeline.process(text, "test-doc-negation")
    
    go_node = next((n for n in graph.nodes if "go" in n.label), None)
    assert go_node is not None
    assert go_node.properties.get("polarity") == "negative"

def test_future_tense():
    """Test that 'will' sets modality to future."""
    pipeline = Pipeline()
    
    text = "I will see you later."
    graph = pipeline.process(text, "test-doc-future")
    
    see_node = next((n for n in graph.nodes if "see" in n.label), None)
    assert see_node is not None
    assert see_node.properties.get("modality") == "future"
