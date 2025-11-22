from app.pipeline import Pipeline

# Debug script to see what nodes are created
pipeline = Pipeline()
text = "I tried but I failed."
graph = pipeline.process(text, "debug-discourse")

print("\n=== NODES ===")
for node in graph.nodes:
    print(f"ID: {node.id}, Type: {node.type}, Label: {node.label}")

print("\n=== EDGES ===")
for edge in graph.edges:
    print(f"Source: {edge.source}, Target: {edge.target}, Role: {edge.role}")
