import pytest
from app.pipeline import Pipeline
from app.models import NodeType, EdgeRole

def test_pipeline_processing():
    pipeline = Pipeline("en_core_web_sm")
    text = "Gregor Samsa awoke from uneasy dreams."
    doc_id = "test_doc_1"
    
    graph = pipeline.process(text, doc_id)
    
    # Check Graph Structure
    assert len(graph.nodes) > 0
    assert len(graph.context_frames) == 1
    assert graph.context_frames[0].source_doc == doc_id
    
    # Check Entities
    entities = [n for n in graph.nodes if n.type == NodeType.ENTITY]
    assert any("Gregor Samsa" in n.label for n in entities)
    
    # Check Events
    events = [n for n in graph.nodes if n.type == NodeType.EVENT]
    assert any("awake" in n.label for n in events) # lemma of awoke
    
    # Check Edges (Gregor -> awoke)
    # "Gregor Samsa" is nsubj of "awoke", so Agent role
    # Note: In our simple pipeline, we might link the entity node or a token node.
    # Let's check if there is an edge with Agent role.
    agent_edges = [e for e in graph.edges if e.role == EdgeRole.AGENT]
    assert len(agent_edges) > 0

if __name__ == "__main__":
    test_pipeline_processing()
