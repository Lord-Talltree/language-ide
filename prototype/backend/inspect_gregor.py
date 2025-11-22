import requests
import json

API_BASE = "http://localhost:8000/v0"

text = "Gregor Samsa awoke from uneasy dreams, he found himself transformed in his bed into a gigantic insect."

def inspect_graph():
    # Create Doc
    resp = requests.post(f"{API_BASE}/docs", json={"text": text, "lang": "en"})
    if resp.status_code != 200: return
    doc_id = resp.json()["id"]
    
    # Analyze
    requests.post(f"{API_BASE}/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map", "stages": ["parse", "graph"]}
    })
    
    # Get Graph
    resp = requests.get(f"{API_BASE}/docs/{doc_id}/graph")
    graph = resp.json()
    
    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")
    
    # Print Entities/Arguments to see if they are distinct
    print("\n--- Argument Nodes ---")
    for n in graph['nodes']:
        if n['type'] == 'Entity':
            print(f"[{n['id']}] {n['label']}")
            
    # Print Edges to see connectivity
    print("\n--- Edges ---")
    for e in graph['edges']:
        src = next(n['label'] for n in graph['nodes'] if n['id'] == e['source'])
        tgt = next(n['label'] for n in graph['nodes'] if n['id'] == e['target'])
        print(f"{src} --{e['role']}--> {tgt}")

if __name__ == "__main__":
    inspect_graph()
