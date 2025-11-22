"""
Session management API endpoints.
Provides CRUD operations and export functionality for sessions.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import json

from app.session_models import SessionMetadata, CreateSessionRequest, UpdateSessionRequest, ExportFormat
from app.storage import get_storage
from app.models import MeaningGraph

router = APIRouter(prefix="/v0/sessions", tags=["sessions"])
storage = get_storage()


@router.get("", response_model=List[SessionMetadata])
async def list_sessions(limit: int = 100, offset: int = 0):
    """List all sessions with metadata."""
    docs = storage.list_documents(limit=limit, offset=offset)
    
    sessions = []
    for doc in docs:
        metadata = storage.get_session_metadata(doc.id)
        if metadata:
            sessions.append(metadata)
    
    return sessions


@router.post("", response_model=SessionMetadata)
async def create_session(request: CreateSessionRequest):
    """Create a new session."""
    session_id = str(uuid.uuid4())
    name = request.name or f"Session {session_id[:8]}"
    
    # Create document
    storage.save_document(session_id, request.text, request.lang)
    
    # Return metadata
    metadata = storage.get_session_metadata(session_id)
    return metadata


@router.get("/{session_id}", response_model=SessionMetadata)
async def get_session(session_id: str):
    """Get session metadata."""
    metadata = storage.get_session_metadata(session_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="Session not found")
    return metadata


@router.patch("/{session_id}", response_model=SessionMetadata)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update session (e.g., rename)."""
    if request.name:
        success = storage.update_session_name(session_id, request.name)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
    
    metadata = storage.get_session_metadata(session_id)
    return metadata


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its graph."""
    deleted = storage.delete_document(session_id)
    return {"status": "deleted" if deleted else "not_found"}


@router.get("/{session_id}/export")
async def export_session(session_id: str, format: str = "json"):
    """Export session as JSON or Markdown."""
    doc = storage.get_document(session_id)
    graph = storage.get_graph(session_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if format == "json":
        return {
            "session_id": session_id,
            "document": doc.dict(),
            "graph": graph.dict() if graph else None
        }
    
    elif format == "markdown":
        return _export_markdown(session_id, doc, graph)
    
    else:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'markdown'")


def _export_markdown(session_id: str, doc, graph: MeaningGraph) -> dict:
    """Generate Markdown export of a session."""
    lines = []
    
    # Header
    lines.append(f"# Session: {session_id}\n")
    lines.append(f"**Created**: {doc.created_at}\n")
    lines.append(f"**Language**: {doc.lang}\n")
    lines.append("\n---\n")
    
    # Original Text
    lines.append("## Original Text\n")
    lines.append(f"{doc.text}\n")
    lines.append("\n---\n")
    
    if graph:
        # Goals
        goals = [n for n in graph.nodes if n.type == "Goal"]
        if goals:
            lines.append("## Goals\n")
            for goal in goals:
                lines.append(f"- **{goal.label}** (ID: {goal.id})\n")
            lines.append("\n")
        
        # Events
        events = [n for n in graph.nodes if n.type == "Event"]
        if events:
            lines.append("## Events\n")
            for event in events:
                lines.append(f"- **{event.label}** (ID: {event.id})\n")
            lines.append("\n")
        
        # Entities
        entities = [n for n in graph.nodes if n.type == "Entity"]
        if entities:
            lines.append("## Entities\n")
            for entity in entities:
                lines.append(f"- **{entity.label}** (ID: {entity.id})\n")
            lines.append("\n")
        
        # Diagnostics
        if graph.diagnostics:
            lines.append("## Diagnostics\n")
            for diag in graph.diagnostics:
                lines.append(f"- **{diag.kind}**: {diag.message}\n")
            lines.append("\n")
    
    markdown_content = "".join(lines)
    
    return {
        "format": "markdown",
        "content": markdown_content
    }
