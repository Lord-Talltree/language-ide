"""
Session-aware analysis API endpoints.

Enables analyzing messages in the context of conversation history,
building an accumulated map that grows with each message.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.storage import get_storage
from app.pipeline import analyze  # Fixed: was analyze_text
from app.models import MeaningGraph
from app.checkers.continuity import ContinuityChecker
from app.checkers.ambiguity import AmbiguityChecker
from app.checkers.oxymoron import OxymoronChecker

router = APIRouter(prefix="/sessions", tags=["session-analysis"])
storage = get_storage()


class AnalyzeMessageRequest(BaseModel):
    text: str
    lang: str = "en"


@router.post("/{session_id}/messages")
async def analyze_session_message(session_id: str, request: AnalyzeMessageRequest):
    """
    Analyze a message in the context of the session history.
    
    This is the core of session-aware analysis:
    1. Get conversation history
    2. Analyze new message
    3. Build accumulated graph
    4. Run checkers on FULL context
    5. Return diagnostics from accumulated view
    """
    
    # Verify session exists
    session_meta = storage.get_session_metadata(session_id)
    if not session_meta:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Analyze the new message
    doc_response = storage.save_document(
        doc_id=f"msg_{session_id}_{len(storage.get_session_messages(session_id))}",
        text=request.text,
        lang=request.lang
    )
    
    # Run pipeline on new message
    new_graph = analyze(request.text, request.lang)
    storage.save_graph(doc_response.id, new_graph)
    
    # Add message to session history
    storage.add_session_message(session_id, request.text, doc_response.id)
    
    # Get accumulated graph (all messages so far)
    accumulated_graph = storage.get_accumulated_graph(session_id)
    
    if not accumulated_graph:
        # Fallback to just the new message
        accumulated_graph = new_graph
    
    # Run checkers on ACCUMULATED graph (this is the key!)
    continuity_checker = ContinuityChecker()
    ambiguity_checker = AmbiguityChecker()
    oxymoron_checker = OxymoronChecker()
    
    # Check for contradictions across the entire conversation
    continuity_diagnostics = continuity_checker.check(accumulated_graph)
    ambiguity_diagnostics = ambiguity_checker.check(accumulated_graph)
    oxymoron_diagnostics = oxymoron_checker.check(accumulated_graph)
    
    # Combine all diagnostics
    all_diagnostics = (
        continuity_diagnostics + 
        ambiguity_diagnostics + 
        oxymoron_diagnostics
    )
    
    # Update accumulated graph with diagnostics
    accumulated_graph.diagnostics = all_diagnostics
    
    return {
        "message_id": doc_response.id,
        "session_id": session_id,
        "graph": accumulated_graph.dict(),
        "diagnostics": [d.dict() for d in all_diagnostics],
        "message_count": len(storage.get_session_messages(session_id))
    }


@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages in a session."""
    messages = storage.get_session_messages(session_id)
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages
    }


@router.get("/{session_id}/accumulated-graph")
async def get_session_accumulated_graph(session_id: str):
    """Get the full accumulated graph for a session."""
    graph = storage.get_accumulated_graph(session_id)
    
    if not graph:
        raise HTTPException(status_code=404, detail="No messages in session")
    
    return {
        "session_id": session_id,
        "graph": graph.dict(),
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "diagnostic_count": len(graph.diagnostics)
    }
