import pytest
from app.pipeline import Pipeline
from app.models import EdgeRole, NodeType

def test_discourse_cause():
    """Test 'because' creates a CAUSE edge."""
    pipeline = Pipeline()
    
    text = "I fell because I tripped."
    graph = pipeline.process(text, "test-doc-cause")
    
    # Should find edge from "tripped" (source) to "fell" (target) with role CAUSE
    # Note: In "A because B", B causes A.
    
    # Find EVENT nodes (not Entity nodes)
    fell_node = next((n for n in graph.nodes if n.type == NodeType.EVENT and ("fall" in n.label or "fell" in n.label)), None)
    trip_node = next((n for n in graph.nodes if n.type == NodeType.EVENT and ("trip" in n.label or "tripped" in n.label)), None)
    
    assert fell_node is not None
    assert trip_node is not None
    
    # Find edge
    cause_edge = next((e for e in graph.edges if e.role == EdgeRole.CAUSE), None)
    assert cause_edge is not None
    
    # Verify direction: tripped -> fell
    assert cause_edge.source == trip_node.id
    assert cause_edge.target == fell_node.id

def test_discourse_contrast():
    """Test 'but' creates a CONTRAST edge."""
    pipeline = Pipeline()
    
    text = "I tried but I failed."
    graph = pipeline.process(text, "test-doc-contrast")
    
    # Find EVENT nodes (not Entity nodes)
    try_node = next((n for n in graph.nodes if n.type == NodeType.EVENT and "try" in n.label), None)
    fail_node = next((n for n in graph.nodes if n.type == NodeType.EVENT and "fail" in n.label), None)
    
    assert try_node is not None
    assert fail_node is not None
    
    contrast_edge = next((e for e in graph.edges if e.role == EdgeRole.CONTRAST), None)
    assert contrast_edge is not None
    
    # Direction for 'but' is usually first -> second
    assert contrast_edge.source == try_node.id
    assert contrast_edge.target == fail_node.id
