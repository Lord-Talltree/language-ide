import spacy
from app.pipeline import get_pipeline
from app.plugins import registry
from plugins.discourse import DiscoursePlugin

def debug():
    text = "I fell because I tripped."
    print(f"Analyzing: '{text}'")
    
    # 1. Check SpaCy output
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    print("Tokens:")
    for token in doc:
        print(f"  {token.text} ({token.pos_}, {token.dep_})")
        
    # 2. Check Pipeline Graph
    pipeline = get_pipeline()
    graph = pipeline.process(text, "debug_doc")
    
    print("\nGraph Nodes:")
    for node in graph.nodes:
        print(f"  {node.id}: {node.label} ({node.type}) Span: {node.span}")
        
    # 3. Run Plugin
    plugin = DiscoursePlugin()
    result = plugin.run(graph, {"doc_id": "debug_doc"})
    
    print("\nPlugin Result:")
    if "graph_updates" in result:
        edges = result["graph_updates"].get("edges", [])
        print(f"  New Edges: {len(edges)}")
        for e in edges:
            print(f"    {e.source} -> {e.target} ({e.role})")
    else:
        print("  No graph updates found.")

if __name__ == "__main__":
    debug()
