from typing import Dict, List, Optional
from app.models import MeaningGraph, Node, Edge, Assertion

class SessionManager:
    """
    Manages the persistent 'World Model' (Meaning Graph) for a chat session.
    """
    def __init__(self):
        self.graph = MeaningGraph(nodes=[], edges=[], assertions=[])
        self.history: List[Dict[str, str]] = [] # Keep track of history with doc_ids

    def update_graph(self, new_graph: MeaningGraph):
        """
        Merges a new graph (from a single turn) into the persistent session graph.
        For MVP, we simply append new nodes/edges/assertions.
        In a real system, we would need entity resolution (merging "Gregor" with "Gregor").
        """
        # Simple merge for MVP
        # Note: This doesn't deduplicate nodes yet, relying on unique IDs from pipeline if possible,
        # but pipeline generates new IDs each run. 
        # TODO: Implement proper entity merging based on labels/coref.
        
        self.graph.nodes.extend(new_graph.nodes)
        self.graph.edges.extend(new_graph.edges)
        self.graph.assertions.extend(new_graph.assertions)
        self.graph.context_frames.extend(new_graph.context_frames) # Ensure frames are merged
        
        # Merge diagnostics? Maybe we only care about current turn diagnostics.
        # self.graph.diagnostics.extend(new_graph.diagnostics)

    def get_graph(self) -> MeaningGraph:
        return self.graph

    def add_history(self, text: str, doc_id: str):
        self.history.append({"text": text, "doc_id": doc_id})

# Singleton instance
_session_instance = None

def get_session():
    global _session_instance
    if _session_instance is None:
        _session_instance = SessionManager()
    return _session_instance
