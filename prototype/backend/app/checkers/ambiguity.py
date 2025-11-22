from typing import List, Dict, Any
from app.models import MeaningGraph, Node, Edge, NodeType, Diagnostic, DiagnosticKind, Severity, Provenance

class AmbiguityChecker:
    """
    Scans the Meaning Graph for vague or ambiguous terms.
    MVP: Detects vague pronouns and generic nouns.
    """
    
    VAGUE_PRONOUNS = {"it", "this", "that", "these", "those", "they"}
    GENERIC_NOUNS = {"thing", "stuff", "item", "object", "file", "code", "function", "class", "data"}

    def check(self, graph: MeaningGraph) -> List[Diagnostic]:
        diagnostics = []
        
        for node in graph.nodes:
            if node.type == NodeType.ENTITY:
                # Check for Vague Pronouns
                if node.label.lower() in self.VAGUE_PRONOUNS:
                    # Check if it has a "Refers_to" or "SameAs" edge
                    has_reference = any(
                        e.source == node.id and e.role in ("Refers_to", "SameAs") 
                        for e in graph.edges
                    )
                    
                    if not has_reference:
                        diagnostics.append(self._create_diagnostic(
                            node, 
                            f"Ambiguous pronoun '{node.label}'. What does '{node.label}' refer to?",
                            Severity.WARNING
                        ))

                # Check for Generic Nouns
                # e.g. "the file" is vague if we don't know WHICH file.
                # Heuristic: If label is just a generic noun with no modifiers or specific properties.
                elif node.label.lower() in self.GENERIC_NOUNS:
                     # Check if it has specific properties or edges that clarify it
                    is_specific = False
                    # (For MVP, we'll be strict: if it's just "file", it's vague)
                    
                    diagnostics.append(self._create_diagnostic(
                        node,
                        f"Vague term '{node.label}'. Which specific {node.label} do you mean?",
                        Severity.INFO
                    ))

        return diagnostics

    def _create_diagnostic(self, node: Node, message: str, severity: Severity) -> Diagnostic:
        return Diagnostic(
            kind=DiagnosticKind.AMBIGUITY,
            severity=severity,
            message=message,
            provenance=[Provenance(
                engine_id="ambiguity-checker",
                engine_version="0.1.0",
                span=node.span
            )]
        )
