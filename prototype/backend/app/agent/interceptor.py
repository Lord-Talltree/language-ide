from typing import Optional
from app.pipeline import Pipeline
from app.agent.session import SessionManager
from app.checkers.continuity import ContinuityChecker
from app.checkers.oxymoron import OxymoronChecker
from app.checkers.ambiguity import AmbiguityChecker
from app.coref import CoreferenceResolver
from app.models import DiagnosticKind

class Interceptor:
    """
    The 'Sidecar' that sits between User and Agent.
    It analyzes user input, updates the session graph, and checks for contradictions.
    """
    def __init__(self):
        self.pipeline = Pipeline()
        self.checker = ContinuityChecker()
        self.oxymoron_checker = OxymoronChecker()
        self.ambiguity_checker = AmbiguityChecker()
        self.resolver = CoreferenceResolver()

    def check_and_inject(self, user_message: str, session: SessionManager) -> Optional[str]:
        """
        Analyzes the user message, updates the session graph, and returns a System Warning
        if a contradiction is detected.
        """
        # 1. Run Pipeline on new message
        # Note: We generate a fresh graph for this turn
        # In a real system, we'd pass the history context to the pipeline/LLM
        import uuid
        doc_id = str(uuid.uuid4())
        turn_graph = self.pipeline.process(user_message, doc_id)

        # 2. Update Session Graph
        session.update_graph(turn_graph)
        session.add_history(user_message, doc_id)

        # 3. Run Coreference Resolution on the FULL Session Graph
        # This links "It" in the new turn to "The building" in previous turns
        full_graph = session.get_graph()
        full_graph = self.resolver.resolve(None, full_graph)

        # 4. Run Continuity Checker on the FULL Session Graph
        # This checks if the new assertions contradict ANY previous assertions
        errors = self.checker.check(full_graph)

        # 5. Run Oxymoron Checker on the TURN Graph
        oxymorons = self.oxymoron_checker.check(turn_graph)
        
        # 6. Run Ambiguity Checker on the TURN Graph
        # We check if the user's NEW input is vague
        ambiguities = self.ambiguity_checker.check(turn_graph)

        # 7. Generate System Warning (Priority Order)
        
        # Priority 1: Oxymorons (Confusion)
        if oxymorons:
            oxy = oxymorons[0]
            try:
                terms_part = oxy.message.split('(')[1].split(')')[0]
                terms = terms_part.replace(' and ', ' ')
            except:
                terms = "contradictory terms"
            
            return (
                f"[SYSTEM WARNING: Contradiction detected. "
                f"I was thinking \"{terms}\" would be unclear, should this sentence make sense?]"
            )

        # Priority 2: Ambiguity (Clarification needed before acting)
        if ambiguities:
            amb = ambiguities[0]
            return f"[SYSTEM WARNING: Ambiguity detected. {amb.message} Please clarify.]"

        # Priority 3: Continuity (History contradiction)
        if errors:
            error = errors[0]
            return (
                f"[SYSTEM WARNING: Contradiction detected in user reasoning. "
                f"User previously implied '{error.subject} {error.property_name} {error.val1}', "
                f"but now implies '{error.val2}'. "
                f"Ask the user to clarify.]"
            )
        
        return None
