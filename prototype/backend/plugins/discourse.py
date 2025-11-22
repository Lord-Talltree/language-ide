from typing import Dict, Any, List
from app.plugins import Plugin
from app.models import MeaningGraph, Edge, EdgeRole, Provenance, Node, NodeType

class DiscoursePlugin(Plugin):
    def __init__(self):
        super().__init__(engine_id="discourse-engine-stub", version="0.1.0")
        self.markers = {
            "because": EdgeRole.CAUSE, # or Support
            "however": EdgeRole.CONTRADICTION,
            "therefore": EdgeRole.SUPPORT,
            "but": EdgeRole.CONTRADICTION
        }

    def run(self, graph: MeaningGraph, context: Dict[str, Any]) -> Dict[str, Any]:
        # Simple heuristic: Look for markers in the text (if available) or nodes
        # Since we don't have the raw text easily accessible here (unless passed in context),
        # we'll look for nodes that might represent these markers or just scan the graph.
        # Ideally, the pipeline should have preserved these as nodes or tokens.
        
        # For this stub, let's assume markers are captured as Event/Entity nodes or we scan the original text if we had it.
        # But we only receive the graph.
        # Let's look for nodes with labels matching markers.
        
        new_edges = []
        
        for node in graph.nodes:
            if node.label.lower() in self.markers:
                role = self.markers[node.label.lower()]
                
                # Heuristic: Link the previous event to the next event
                # Find events before and after this node based on span
                if not node.span:
                    continue
                    
                prev_event = None
                next_event = None
                
                # Find closest event before
                events = [n for n in graph.nodes if n.type == NodeType.EVENT and n.span]
                events.sort(key=lambda x: x.span.start)
                
                for i, evt in enumerate(events):
                    if evt.span.end < node.span.start:
                        prev_event = evt
                    elif evt.span.start > node.span.end:
                        next_event = evt
                        break # Found the first one after
                
                if prev_event and next_event:
                    # Create edge: Next -> Prev (e.g. "I fell because I tripped" -> Tripped CAUSE Fell)
                    # Or Prev -> Next (e.g. "I tripped therefore I fell" -> Tripped SUPPORT Fell)
                    
                    source = prev_event.id
                    target = next_event.id
                    
                    if node.label.lower() == "because":
                        # "A because B" -> B CAUSE A
                        source = next_event.id
                        target = prev_event.id
                    
                    new_edges.append(Edge(
                        source=source,
                        target=target,
                        role=role,
                        provenance=[Provenance(
                            engine_id=self.engine_id,
                            engine_version=self.version,
                            source_doc=context.get("doc_id")
                        )]
                    ))
        
        # We can't easily modify the graph in place in the run method return, 
        # but the contract says we return diagnostics/validations.
        # The contract in `plugins.py` says return Dict with diagnostics, etc.
        # It doesn't explicitly allow returning new edges/nodes to merge.
        # But `TruthInterpreter` logic I wrote only merges diagnostics.
        # I should update `TruthInterpreter` to merge edges too if I want this to work.
        # Or just return diagnostics saying "Discourse relation detected".
        
        # Let's return diagnostics for now to be safe, or update the interpreter.
        # I'll update the interpreter to merge edges.
        
        # But first, return the edges in a custom key "graph_updates"
        return {
            "graph_updates": {"edges": new_edges}
        }
