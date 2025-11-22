from typing import List, Dict, Tuple, Any
from app.models import MeaningGraph, Assertion

class LogicEngine:
    def __init__(self, graph: MeaningGraph):
        self.graph = graph
        self.assertions = graph.assertions

    def find_contradictions(self) -> List[Dict[str, Any]]:
        """
        Finds potential contradictions in the assertions.
        Current heuristic: Same Subject + Same Predicate + Different Object
        (excluding cases where object is None, or Modality differs significantly)
        """
        contradictions = []
        seen: Dict[Tuple[str, str], Assertion] = {}

        for assertion in self.assertions:
            # Key: (Subject, Predicate)
            # We normalize to lower case for looser matching
            key = (assertion.subject.lower(), assertion.predicate.lower())
            
            if key in seen:
                prev_assertion = seen[key]
                
                # Check for conflict
                # 1. Objects must differ
                # 2. Neither object should be None (unless one implies absence?)
                # 3. Conditions should be similar (if one is conditional and other is not, it might not be a contradiction)
                
                obj1 = prev_assertion.object
                obj2 = assertion.object
                
                if obj1 and obj2 and obj1.lower() != obj2.lower():
                    # Potential contradiction
                    # Check conditions
                    cond1 = prev_assertion.condition
                    cond2 = assertion.condition
                    
                    # If conditions are different, they might not contradict (e.g. "If rain, stay. If sun, go.")
                    if cond1 == cond2:
                        contradictions.append({
                            "type": "DirectConflict",
                            "assertion_1": prev_assertion,
                            "assertion_2": assertion,
                            "reason": f"Conflicting objects: '{obj1}' vs '{obj2}'"
                        })
            else:
                seen[key] = assertion
                
        return contradictions

    def find_open_questions(self) -> List[Dict[str, Any]]:
        """
        Identifies open questions or unverified assumptions based on conditions.
        """
        open_questions = []
        for assertion in self.assertions:
            if assertion.condition:
                open_questions.append({
                    "type": "ConditionalAssumption",
                    "assertion": assertion,
                    "question": f"Is it true that '{assertion.condition}'?"
                })
            elif assertion.modality and assertion.modality.lower() in ("might", "may", "could", "assume"):
                 open_questions.append({
                    "type": "Uncertainty",
                    "assertion": assertion,
                    "question": f"Verify if '{assertion.subject}' really '{assertion.predicate}' '{assertion.object}'."
                })
                
        return open_questions
