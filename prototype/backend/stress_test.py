import requests
import json
import time

API_BASE = "http://localhost:8000/v0"

sentences = [
    "If the server is down, the client should retry three times.",
    "The user must be logged in to access the dashboard, unless they have an admin token.",
    "Processing large files requires significant memory and can slow down the system.",
    "The quick brown fox jumps over the lazy dog.",
    "Alice said that Bob thinks that Charlie is late."
]

def analyze_text(text):
    print(f"\n--- Analyzing: '{text}' ---")
    # 1. Create Doc
    res = requests.post(f"{API_BASE}/docs", json={"text": text, "lang": "en"})
    if res.status_code != 200:
        print(f"Error creating doc: {res.text}")
        return
    doc_id = res.json()["id"]
    
    # 2. Analyze
    res = requests.post(f"{API_BASE}/analyze", json={
        "docId": doc_id,
        "options": {
            "processing_mode": "Map",
            "stages": ["segment", "parse", "graph"],
            "detail": "full"
        }
    })
    if res.status_code != 200:
        print(f"Error analyzing: {res.text}")
        return
    
    # 3. Get Graph
    res = requests.get(f"{API_BASE}/docs/{doc_id}/graph")
    if res.status_code != 200:
        print(f"Error getting graph: {res.text}")
        return
    
    graph = res.json()
    if "graph_summary" not in graph:
        print(f"Unexpected response: {graph}")
        return
        
    nodes = graph["graph_summary"]["nodes"]
    edges = graph["graph_summary"]["edges"]
    print(f"Nodes: {nodes}, Edges: {edges}")
    
    # Print Edges for detail
    full_graph = res.json() # The summary is just counts, let's look at the full response structure if available?
    # Wait, the endpoint returns the full graph, but I'm printing summary.
    # Let's print the actual edges from the full response if I can parse them.
    # The response model for get_graph returns MeaningGraph.
    # Let's print the edges list.
    
    print("Edges:")
    for edge in graph.get("edges", []):
        print(f"  {edge['source']} -> {edge['target']} ({edge['role']})")

if __name__ == "__main__":
    for s in sentences:
        analyze_text(s)
        time.sleep(0.5)
