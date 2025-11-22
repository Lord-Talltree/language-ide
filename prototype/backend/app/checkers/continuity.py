from typing import List, Dict
from app.models import MeaningGraph, Assertion, Node

class ContinuityError:
    def __init__(self, subject: str, property_name: str, val1: str, val2: str, span1: Dict, span2: Dict):
        self.subject = subject
        self.property_name = property_name
        self.val1 = val1
        self.val2 = val2
        self.span1 = span1
        self.span2 = span2
        self.message = f"Continuity Error: {subject} has '{property_name}' as '{val1}' and later as '{val2}'."

    def to_dict(self):
        return {
            "kind": "ContinuityError",
            "message": self.message,
            "details": {
                "subject": self.subject,
                "property": self.property_name,
                "conflict": f"{self.val1} vs {self.val2}"
            }
        }

class ContinuityChecker:
    def check(self, graph: MeaningGraph) -> List[ContinuityError]:
        errors = []
        
        # 1. Build Canonical Entity Map from SameAs edges
        # Map: entity_id -> canonical_entity_id
        canonical_map = {}
        for edge in graph.edges:
            if edge.role == "SameAs":
                # If A -> B (SameAs), then A maps to B
                # We should ideally handle chains (A->B->C), but 1-hop is fine for prototype
                canonical_map[edge.source] = edge.target

        # Helper to resolve subject to canonical ID
        def resolve_subject(subj_id_or_label):
            # Try to find node by label if passed as label (assertions store labels currently?)
            # The Assertion model stores 'subject' as string label usually.
            # But we need to link it back to the Node ID to check edges.
            
            # Let's assume for this prototype that we can find the node by label
            # Or better, let's look at how assertions are created. 
            # They seem to use labels. This is a weakness in the current AssertionExtractor.
            # It should probably use IDs.
            
            # Workaround: Find node with this label
            # (This is ambiguous if multiple "buildings" exist, but acceptable for prototype)
            node = next((n for n in graph.nodes if n.label == subj_id_or_label), None)
            if node:
                # Check if this node maps to another
                if node.id in canonical_map:
                    target_id = canonical_map[node.id]
                    target_node = next((n for n in graph.nodes if n.id == target_id), None)
                    if target_node:
                        return target_node.label
            return subj_id_or_label

        # 2. Group assertions by Canonical Subject -> Predicate
        # Structure: { "Gregor": { "eye_color": [ {val: "blue", span: ...}, {val: "brown", span: ...} ] } }
        entity_properties: Dict[str, Dict[str, List[Dict]]] = {}

        for assertion in graph.assertions:
            raw_subj = assertion.subject
            subj = resolve_subject(raw_subj) # Resolve to canonical
            
            pred = assertion.predicate
            obj = assertion.object
            
            if subj not in entity_properties:
                entity_properties[subj] = {}
            
            if pred not in entity_properties[subj]:
                entity_properties[subj][pred] = []
                
            entity_properties[subj][pred].append({
                "value": obj,
                "span": None 
            })

        # 2. Detect Conflicts
        for subj, props in entity_properties.items():
            for pred, values in props.items():
                if len(values) > 1:
                    # Check if values are different
                    first_val = values[0]["value"]
                    for i in range(1, len(values)):
                        curr_val = values[i]["value"]
                        if curr_val != first_val:
                            # Found a conflict!
                            errors.append(ContinuityError(
                                subject=subj,
                                property_name=pred,
                                val1=first_val,
                                val2=curr_val,
                                span1=values[0]["span"],
                                span2=values[i]["span"]
                            ))
                            
        return errors
