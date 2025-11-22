from typing import List, Dict, Any
from app.models import (
    AmbiguitySet, AmbiguityDimension, AmbiguityAlternative, 
    Diagnostic, DiagnosticKind, Severity, Provenance, Span
)
import uuid

class AmbiguityManager:
    def __init__(self):
        self.engine_id = "rule-based-ambiguity"
        self.version = "0.1.0"

    def detect_ambiguities(self, text: str, doc_id: str) -> tuple[List[AmbiguitySet], List[Diagnostic]]:
        ambiguity_sets = []
        diagnostics = []
        
        # 1. Vagueness Detection (Rule-based for prototype)
        # Example: "uneasy" in Kafka's sentence
        vague_terms = ["uneasy", "somewhat", "possibly", "maybe"]
        for term in vague_terms:
            if term in text.lower():
                start_idx = text.lower().find(term)
                if start_idx != -1:
                    end_idx = start_idx + len(term)
                    diagnostics.append(Diagnostic(
                        kind=DiagnosticKind.VAGUENESS,
                        severity=Severity.INFO,
                        message=f"Term '{term}' is potentially vague.",
                        provenance=[Provenance(
                            engine_id=self.engine_id,
                            engine_version=self.version,
                            source_doc=doc_id,
                            span=Span(start=start_idx, end=end_idx, text=text[start_idx:end_idx])
                        )]
                    ))

        # 2. Figurative vs Literal Ambiguity (Kafka Example)
        # "transformed into a gigantic insect"
        if "transformed" in text.lower() and "insect" in text.lower():
            # Create AmbiguitySet for the transformation
            amb_id = f"amb_{uuid.uuid4().hex[:8]}"
            amb_set = AmbiguitySet(
                id=amb_id,
                dimension=AmbiguityDimension.AMB_FIG,
                alternatives=[
                    AmbiguityAlternative(
                        label="Literal Transformation",
                        weight=0.4,
                        delta={"add_edges": [{"role": "Theme", "target": "insect"}]} # Simplified delta
                    ),
                    AmbiguityAlternative(
                        label="Figurative (Metaphor)",
                        weight=0.6,
                        delta={"add_edges": [{"role": "Refers_to", "target": "mental_state"}]} # Simplified delta
                    )
                ],
                provenance=[Provenance(
                    engine_id=self.engine_id,
                    engine_version=self.version,
                    source_doc=doc_id
                )]
            )
            ambiguity_sets.append(amb_set)
            
        return ambiguity_sets, diagnostics
