import requests
import json
import sys
import os

# Add parent dir to path to import app modules directly if needed, 
# but we will test via API if possible? 
# Actually, LogicEngine is a backend class. We haven't exposed it via API yet.
# So we should test it by importing it, OR expose it via API.
# Let's expose it via API first? Or just test the class directly using the models?
# Testing the class directly is faster for unit testing.

# We need to mock the graph or fetch it.
# Let's use the API to get the graph, then instantiate LogicEngine locally (since we are in the same repo).

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import MeaningGraph, Assertion
from app.logic import LogicEngine

# Helper to fetch graph from API (running server)
API_BASE = "http://localhost:8000/v0"

def get_graph_from_text(text):
    resp = requests.post(f"{API_BASE}/docs", json={"text": text, "lang": "en"})
    if resp.status_code != 200: return None
    doc_id = resp.json()["id"]
    
    resp = requests.post(f"{API_BASE}/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map", "stages": ["parse", "graph"]}
    })
    if resp.status_code != 200: return None
    
    resp = requests.get(f"{API_BASE}/docs/{doc_id}/graph")
    if resp.status_code != 200: return None
    return resp.json()

def run_test():
    print("--- Testing Logic Engine ---")
    
    # Case 1: Contradiction
    text1 = "The server is live. The server is down."
    print(f"\nInput: {text1}")
    graph_data = get_graph_from_text(text1)
    if graph_data:
        # Reconstruct Assertion objects from JSON
        raw_assertions = graph_data.get('assertions', [])
        print("DEBUG: Extracted Assertions:")
        for a in raw_assertions:
            print(f"  {a}")
            
        print("DEBUG: Raw Edges:")
        for e in graph_data.get('edges', []):
            print(f"  {e['source']} --{e['role']}--> {e['target']}")
            
        assertions = [Assertion(**a) for a in raw_assertions]
        # Mock Graph (we only need assertions for LogicEngine for now)
        mock_graph = MeaningGraph(nodes=[], edges=[], assertions=assertions) 
        
        engine = LogicEngine(mock_graph)
        contradictions = engine.find_contradictions()
        
        print(f"Contradictions Found: {len(contradictions)}")
        for c in contradictions:
            print(f"  - {c['reason']}")
            
    # Case 2: Open Questions
    text2 = "If the database fails, retry the connection."
    print(f"\nInput: {text2}")
    graph_data = get_graph_from_text(text2)
    if graph_data:
        assertions = [Assertion(**a) for a in graph_data.get('assertions', [])]
        mock_graph = MeaningGraph(nodes=[], edges=[], assertions=assertions)
        
        engine = LogicEngine(mock_graph)
        questions = engine.find_open_questions()
        
        print(f"Open Questions Found: {len(questions)}")
        for q in questions:
            print(f"  - {q['question']}")

if __name__ == "__main__":
    run_test()
