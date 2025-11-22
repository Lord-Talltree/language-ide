from typing import List, Tuple
from app.models import MeaningGraph, Diagnostic, DiagnosticKind, Severity, Provenance

class OxymoronChecker:
    """
    Checks for semantic contradictions (oxymorons) within a single node's label.
    e.g. "tall short building", "deafening silence", "open secret".
    """
    
    def __init__(self):
        # Simple antonym pairs for prototype
        self.antonyms = [
            ({"tall", "short"}, "height"),
            ({"big", "small"}, "size"),
            ({"hot", "cold"}, "temperature"),
            ({"fast", "slow"}, "speed"),
            ({"heavy", "light"}, "weight"),
            ({"dark", "light"}, "brightness"),
            ({"happy", "sad"}, "emotion"),
            ({"good", "bad"}, "quality"),
            ({"true", "false"}, "truth"),
            ({"dead", "alive"}, "state"),
            ({"open", "closed"}, "state"),
            ({"wet", "dry"}, "state"),
            ({"hard", "soft"}, "texture"),
            ({"loud", "quiet"}, "volume"),
            ({"young", "old"}, "age"),
            ({"new", "old"}, "age"),
        ]

    def check(self, graph: MeaningGraph) -> List[Diagnostic]:
        diagnostics = []
        
        for node in graph.nodes:
            # Tokenize label - split on both spaces AND hyphens
            # This allows detection of "tall-short" as well as "tall short"
            import re
            words = set(w.lower() for w in re.split(r'[\s\-]+', node.label) if w)
            
            for pair, category in self.antonyms:
                # Check if both words in the pair exist in the label
                if pair.issubset(words):
                    # Found an oxymoron!
                    diagnostics.append(Diagnostic(
                        kind=DiagnosticKind.CONTRADICTION,
                        message=f"The phrase '{node.label}' contains contradictory terms ({' and '.join(pair)}).",
                        severity=Severity.WARNING,
                        provenance=[Provenance(
                            engine_id="oxymoron-checker",
                            engine_version="1.0",
                            confidence=0.9
                        )]
                    ))
                    
        return diagnostics
