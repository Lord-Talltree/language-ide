from typing import Dict, Any, List
from app.plugins import Plugin
from app.models import MeaningGraph, Diagnostic, DiagnosticKind, Severity, Provenance, Node, NodeType, EdgeRole

class TruthCheckerPlugin(Plugin):
    def __init__(self):
        super().__init__(engine_id="truth-checker-stub", version="0.1.0")
        # Simple Knowledge Base
        self.kb = {
            "human_transform_insect": {
                "premise": "Humans cannot biologically transform into insects.",
                "verdict": "Implausible"
            }
        }

    def run(self, graph: MeaningGraph, context: Dict[str, Any]) -> Dict[str, Any]:
        diagnostics = []
        knowledge_validations = []
        receipts = []

        # Check for "transformed into insect" pattern
        # In a real system, this would be a graph query
        # Here we look for Event(transform) -> Theme(insect)
        
        transform_events = [n for n in graph.nodes if n.type == NodeType.EVENT and "transform" in n.label.lower()]
        
        for evt in transform_events:
            # Find edges from this event
            edges = [e for e in graph.edges if e.source == evt.id]
            
            # Check if target is insect-related
            for edge in edges:
                target_node = next((n for n in graph.nodes if n.id == edge.target), None)
                if target_node and "insect" in target_node.label.lower():
                    # Found the pattern
                    kb_entry = self.kb["human_transform_insect"]
                    
                    diagnostics.append(Diagnostic(
                        kind=DiagnosticKind.KNOWLEDGE_GAP, # or Contradiction
                        severity=Severity.WARNING,
                        message=f"Validation Warning: {kb_entry['premise']}",
                        provenance=[Provenance(
                            engine_id=self.engine_id,
                            engine_version=self.version,
                            source_doc=context.get("doc_id"),
                            receipts=[{"kb_key": "human_transform_insect", "verdict": kb_entry["verdict"]}]
                        )]
                    ))
                    
                    knowledge_validations.append({
                        "check_type": "plausibility",
                        "verdict": kb_entry["verdict"],
                        "rationale": kb_entry["premise"]
                    })

        return {
            "diagnostics": diagnostics,
            "knowledge_validations": knowledge_validations,
            "receipts": receipts
        }
