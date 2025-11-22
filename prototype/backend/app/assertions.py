from typing import List, Dict, Optional
from app.models import MeaningGraph, Node, Edge, NodeType, EdgeRole, Assertion

class AssertionExtractor:
    def extract(self, graph: MeaningGraph) -> List[Assertion]:
        assertions = []
        
        # Index nodes by ID for easy lookup
        node_map = {n.id: n for n in graph.nodes}
        
        # Group edges by source (Event)
        event_edges: Dict[str, List[Edge]] = {}
        for edge in graph.edges:
            if edge.source not in event_edges:
                event_edges[edge.source] = []
            event_edges[edge.source].append(edge)
            
        # Iterate over Event nodes to build assertions
        for node in graph.nodes:
            if node.type == NodeType.EVENT:
                event_id = node.id
                edges = event_edges.get(event_id, [])
                
                # Find Subject (Agent)
                agent_edge = next((e for e in edges if e.role == EdgeRole.AGENT), None)
                subject = node_map[agent_edge.target].label if agent_edge and agent_edge.target in node_map else "Unknown"
                
                # Find Object (Patient/Theme/Location/Time)
                # Priority: Patient > Theme > Location > Time
                object_edge = next((e for e in edges if e.role in (EdgeRole.PATIENT, EdgeRole.THEME)), None)
                
                # If no direct object, look for Location/Time (often prepositional)
                if not object_edge:
                    object_edge = next((e for e in edges if e.role in (EdgeRole.LOCATION, EdgeRole.TIME)), None)
                
                # If still no object, check for 'acomp' (Adjectival Complement) which might be mapped to THEME or SUPPORT depending on pipeline
                # In "The server is down", 'down' is acomp.
                # Let's check if we have any edge to a node that is an ADJ?
                # Or check if we have a Theme edge that we missed?
                # Actually, let's look for ANY edge that isn't Agent/Condition/Sequence/Support if we haven't found an object.
                # Or specifically look for the 'Theme' role again, but maybe the target wasn't in node_map?
                # Wait, in the debug output, the second assertion had object: None.
                # This means object_edge was None.
                # So "down" was NOT linked with Patient/Theme/Location/Time.
                # In pipeline.py, 'acomp' maps to EdgeRole.THEME.
                # So why didn't we find it?
                # Ah, maybe "down" wasn't created as a node?
                # Pipeline creates nodes for: ents, events, and children of events.
                # "down" is a child of "is". It should be a node.
                # Let's broaden the search for object to include 'acomp' if we can find the edge role?
                # But we only have the EdgeRole enum.
                # Let's assume 'acomp' was mapped to THEME.
                # If it was mapped to THEME, why didn't we find it?
                # Maybe the node ID lookup failed?
                # Let's try to be more robust: if no object found, look for ANY other edge target that isn't the subject.
                
                if not object_edge:
                     # Fallback: Find any edge that is NOT Agent, Condition, Sequence, Support
                     object_edge = next((e for e in edges if e.role not in (EdgeRole.AGENT, EdgeRole.CONDITION, EdgeRole.SEQUENCE, EdgeRole.SUPPORT)), None)

                obj = None
                if object_edge and object_edge.target in node_map:
                    obj_node = node_map[object_edge.target]
                    obj_label = obj_node.label
                    
                    # Look for adjectival modifiers (children of the object node)
                    # We need to find edges where source == obj_node.id
                    # Let's scan graph.edges (inefficient but fine for prototype)
                    modifiers = []
                    for mod_edge in graph.edges:
                        if mod_edge.source == obj_node.id:
                            if mod_edge.target in node_map:
                                mod_node = node_map[mod_edge.target]
                                # Check if it's an adjective (heuristic)
                                # We stored 'pos' in properties
                                if mod_node.properties.get("pos") == "ADJ":
                                    modifiers.append(mod_node.label)
                    
                    # Prepend modifiers to object label
                    if modifiers:
                        # Sort modifiers by span start if possible, but for now just join
                        # "blue" + " " + "eyes"
                        obj = f"{' '.join(modifiers)} {obj_label}"
                    else:
                        obj = obj_label
                    
                    # Find Modality (Auxiliary verbs often captured in label or properties, 
                    # but for now let's check if the event label itself implies modality or if we have a 'Support' edge to a modal)
                    # Simplified: Check if label is a modal (e.g. "must", "can") - usually these are Aux, but our parser might treat them as events or support.
                    # Better: Check properties or specific edges. 
                    modality = None
                    
                    # Find Condition
                    condition_edge = next((e for e in edges if e.role == EdgeRole.CONDITION), None)
                    condition = node_map[condition_edge.target].label if condition_edge and condition_edge.target in node_map else None
                    
                    # Construct Assertion
                    assertion = Assertion(
                        subject=subject,
                        predicate=node.label,
                        object=obj,
                        modality=modality,
                        condition=condition,
                        source_event_id=event_id
                    )
                    assertions.append(assertion)
                
        return assertions
