import requests
import json
import time

API_BASE = "http://localhost:8000/v0"

def create_doc(text):
    response = requests.post(f"{API_BASE}/docs", json={"text": text, "lang": "en"})
    if response.status_code != 200:
        print(f"Error creating doc: {response.text}")
        return None
    return response.json()["id"]

def analyze_doc(doc_id):
    response = requests.post(f"{API_BASE}/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map", "stages": ["parse", "graph"]}
    })
    if response.status_code != 200:
        print(f"Error analyzing doc: {response.text}")
        return False
    return True

def get_graph(doc_id):
    response = requests.get(f"{API_BASE}/docs/{doc_id}/graph")
    if response.status_code != 200:
        print(f"Error getting graph: {response.text}")
        return None
    return response.json()

def print_graph_summary(graph, title):
    print(f"\n--- {title} ---")
    if not graph:
        print("No graph data.")
        return

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    
    print(f"Nodes: {len(nodes)}")
    for n in nodes:
        print(f"  [{n['type']}] {n['label']} ({n['id']})")
        
    print(f"Edges: {len(edges)}")
    for e in edges:
        print(f"  {e['source']} --{e['role']}--> {e['target']}")

def run_test(text, title):
    print(f"\nRunning Test: {title}")
    doc_id = create_doc(text)
    if not doc_id: return
    
    if analyze_doc(doc_id):
        graph = get_graph(doc_id)
        print_graph_summary(graph, title)
    else:
        print("Analysis failed.")

# Test Cases
tests = [
    {
        "title": "Simple Action",
        "text": "I woke up."
    },
    {
        "title": "Sequential Action (Time)",
        "text": "I woke up, then I drank coffee."
    },
    {
        "title": "Conditional Logic",
        "text": "If it rains, I will stay home."
    },
    {
        "title": "Complex Project Plan",
        "text": "The frontend team must wait for the API schema before they can start. Sarah needs to update the docs by Friday."
    },
    {
        "title": "Long Text (Paragraph)",
        "text": "The project manager called a meeting to discuss the roadmap. Everyone agreed that the timeline was too tight. However, the CEO insisted on the original deadline. Consequently, the team decided to cut features."
    }
]

# Run standard tests
for t in tests:
    run_test(t["text"], t["title"])

# Run Large Text Test
large_text = "This is sentence number 1. " * 100
print(f"\nRunning Test: Large Text ({len(large_text)} chars)")
start_time = time.time()
doc_id = create_doc(large_text)
if doc_id:
    if analyze_doc(doc_id):
        graph = get_graph(doc_id)
        duration = time.time() - start_time
        print(f"Large text processed in {duration:.2f} seconds.")
        print(f"Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
    else:
        print("Large text analysis failed.")
