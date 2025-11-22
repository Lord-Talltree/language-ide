import requests
import json

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

def run_test(text, title):
    print(f"\n--- Test: {title} ---")
    print(f"Input: \"{text}\"")
    
    doc_id = create_doc(text)
    if not doc_id: return
    
    if analyze_doc(doc_id):
        graph = get_graph(doc_id)
        assertions = graph.get("assertions", [])
        
        print(f"Assertions Found: {len(assertions)}")
        for a in assertions:
            print(f"  - [{a['subject']}] --({a['predicate']})--> [{a['object'] or 'None'}]")
            if a.get('condition'):
                print(f"    Condition: {a['condition']}")
            if a.get('modality'):
                print(f"    Modality: {a['modality']}")
    else:
        print("Analysis failed.")

# Test Cases
tests = [
    {
        "title": "Simple Assertion",
        "text": "The server is live."
    },
    {
        "title": "Conditional Assertion",
        "text": "If it rains, I stay home."
    },
    {
        "title": "Project Dependency",
        "text": "The team must wait for the API before starting."
    }
]

for t in tests:
    run_test(t["text"], t["title"])
