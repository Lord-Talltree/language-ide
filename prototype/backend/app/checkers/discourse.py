from typing import List, Dict, Any
from app.models import MeaningGraph, Node, Edge, EdgeRole, NodeType, Provenance

class DiscourseChecker:
    """
    Scans the graph and text for discourse markers to link events.
    Detects:
    - CAUSE: "because", "since", "therefore"
    - CONTRAST: "however", "but", "although"
    - SEQUENCE: "then", "after", "before"
    """
    
    def check(self, graph: MeaningGraph, doc: Any) -> List[Edge]:
        new_edges = []
        
        # We need to look at the dependency parse (doc) to find markers connecting verbs
        # Iterate over tokens in the doc
        for token in doc:
            # Check for markers
            marker = token.text.lower()
            role = None
            
            if marker in ("because", "since", "so", "therefore"):
                role = EdgeRole.CAUSE
            elif marker in ("but", "however", "although", "though"):
                role = EdgeRole.CONTRAST
            elif marker in ("then", "after", "before"):
                role = EdgeRole.SEQUENCE
                
            if role:
                # If we found a marker, we need to find the two events it connects.
                # Usually markers connect two clauses.
                # Case 1: "A because B" (mark dependency)
                # In spacy: B -> mark -> because. B is the head of the clause.
                # B is attached to A via 'advcl' or similar.
                
                # Let's look at the head of the marker
                head = token.head
                
                # If the marker is "mark" (subordinate clause marker)
                # e.g. "I fell because I tripped"
                # tripped -> mark -> because
                # fell -> advcl -> tripped
                if token.dep_ == "mark":
                    cause_event_token = head # "tripped"
                    effect_event_token = head.head # "fell"
                    
                    # Find corresponding nodes
                    cause_node = self._find_event_node(graph, cause_event_token.i)
                    effect_node = self._find_event_node(graph, effect_event_token.i)
                    
                    if cause_node and effect_node:
                        # For "because", the sub-clause is the CAUSE
                        # fell (Target) <- CAUSE - tripped (Source)
                        if role == EdgeRole.CAUSE:
                            source = cause_node
                            target = effect_node
                        else:
                            # For others, it might be different, but let's stick to flow
                            source = effect_node
                            target = cause_node
                            
                        new_edges.append(Edge(
                            source=source.id,
                            target=target.id,
                            role=role,
                            provenance=[Provenance(engine_id="discourse-checker", engine_version="0.1.0")]
                        ))

                # Case 2: "A. Therefore, B." (Sentence start)
                # This requires cross-sentence logic which is harder.
                # MVP: Focus on intra-sentence "mark" and "cc" (coordinating conjunction)
                
                elif token.dep_ == "cc":
                    # "I tried but I failed"
                    # tried -> cc -> but
                    # tried -> conj -> failed
                    
                    event1_token = head # "tried"
                    # Find the conjunct
                    event2_token = next((c for c in head.children if c.dep_ == "conj"), None)
                    
                    if event2_token:
                        node1 = self._find_event_node(graph, event1_token.i)
                        node2 = self._find_event_node(graph, event2_token.i)
                        
                        if node1 and node2:
                            new_edges.append(Edge(
                                source=node1.id,
                                target=node2.id,
                                role=role,
                                provenance=[Provenance(engine_id="discourse-checker", engine_version="0.1.0")]
                            ))

        return new_edges

    def _find_event_node(self, graph: MeaningGraph, token_index: int) -> Node:
        """Find the Event node corresponding to a token index."""
        # Try both evt_N and tok_N patterns since pipeline creates both
        target_ids = [f"evt_{token_index}", f"tok_{token_index}"]
        
        for node in graph.nodes:
            if node.type == NodeType.EVENT and node.id in target_ids:
                return node
        return None
