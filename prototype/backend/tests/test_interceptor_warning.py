import pytest
from unittest.mock import MagicMock
from app.agent.interceptor import Interceptor
from app.agent.session import SessionManager
from app.models import MeaningGraph, Diagnostic, DiagnosticKind, Severity

def test_interceptor_ambiguity_warning():
    """Test that Interceptor generates the correct warning format for ambiguities."""
    interceptor = Interceptor()
    session = MagicMock(spec=SessionManager)
    
    # Mock session.get_graph to return empty graph (for coref/continuity)
    session.get_graph.return_value = MeaningGraph()
    
    # Mock pipeline.process to return a graph with ambiguity diagnostic
    # But Interceptor runs check_and_inject which runs pipeline.process internally
    # AND runs ambiguity_checker.check manually.
    
    # Let's just test the check_and_inject method with a real pipeline/checker
    # since we want to verify the integration.
    
    user_message = "Check the file."
    warning = interceptor.check_and_inject(user_message, session)
    
    assert warning is not None
    assert "[SYSTEM WARNING:" in warning
    assert "Ambiguity detected" in warning
    assert "Vague term 'file'" in warning
    assert "Please clarify" in warning

def test_interceptor_pronoun_warning():
    """Test warning for vague pronoun."""
    interceptor = Interceptor()
    session = MagicMock(spec=SessionManager)
    session.get_graph.return_value = MeaningGraph()
    
    user_message = "It is broken."
    warning = interceptor.check_and_inject(user_message, session)
    
    assert warning is not None
    assert "Ambiguous pronoun 'It'" in warning
