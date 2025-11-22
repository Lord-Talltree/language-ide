import requests
import json

API_BASE = "http://localhost:8000/v0"

def analyze_text(text):
    # Create Doc
    resp = requests.post(f"{API_BASE}/docs", json={"text": text, "lang": "en"})
    if resp.status_code != 200: return None
    doc_id = resp.json()["id"]
    
    # Analyze
    resp = requests.post(f"{API_BASE}/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map", "stages": ["parse", "graph"]}
    })
    if resp.status_code != 200: return None
    
    # Get Graph
    resp = requests.get(f"{API_BASE}/docs/{doc_id}/graph")
    if resp.status_code != 200: return None
    return resp.json()

def check_contradiction(assertions):
    # Simple heuristic: Look for same subject/predicate but different object/modality
    # Or direct negation (not handled yet, but let's see what we get)
    seen = {}
    conflicts = []
    
    for a in assertions:
        key = (a['subject'], a['predicate'])
        if key in seen:
            prev = seen[key]
            if prev['object'] != a['object']:
                conflicts.append((prev, a))
        else:
            seen[key] = a
            
    return conflicts

tests = [
    {
        "name": "Direct Contradiction",
        "text": "The server is live. The server is down."
    },
    {
        "name": "Temporal Conflict",
        "text": "The meeting is at 2pm. The meeting is at 4pm."
    },
    {
        "name": "Complex Condition",
        "text": "If the database fails, retry the connection. If the database fails, abort the transaction."
    }
]

for t in tests:
    print(f"\n=== Test: {t['name']} ===")
    print(f"Input: {t['text']}")
    graph = analyze_text(t['text'])
    if not graph:
        print("Analysis failed")
        continue
        
    assertions = graph.get("assertions", [])
    print(f"Assertions ({len(assertions)}):")
    for a in assertions:
        print(f"  {a['subject']} --{a['predicate']}--> {a['object']} (Cond: {a['condition']})")
        
    conflicts = check_contradiction(assertions)
    if conflicts:
        print("\n[!] Potential Conflicts Detected:")
        for c in conflicts:
            print(f"  Conflict: '{c[0]['object']}' vs '{c[1]['object']}' for {c[0]['subject']} {c[0]['predicate']}")
    else:
        print("\nNo obvious conflicts detected by simple heuristic.")
