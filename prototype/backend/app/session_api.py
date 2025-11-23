"""
Session management API endpoints.
Provides CRUD operations and export functionality for sessions.
"""

from fastapi import APIRouter, HTTPException
from typing import List
import uuid
import json
from datetime import datetime

from app.session_models import SessionMetadata, CreateSessionRequest, UpdateSessionRequest, ExportFormat
from app.storage import get_storage
from app.models import MeaningGraph

router = APIRouter(prefix="/sessions", tags=["sessions"])
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
    """Generate enhanced Markdown export with hierarchy and edges."""
    lines = []
    
    # Header with metadata
    lines.append(f"# Session Export: {session_id}\n\n")
    lines.append("## Metadata\n\n")
    lines.append(f"- **Session ID**: `{session_id}`\n")
    lines.append(f"- **Created**: {doc.created_at}\n")
    lines.append(f"- **Language**: {doc.lang}\n")
    if graph:
        lines.append(f"- **Nodes**: {len(graph.nodes)}\n")
        lines.append(f"- **Edges**: {len(graph.edges)}\n")
        lines.append(f"- **Diagnostics**: {len(graph.diagnostics)}\n")
    lines.append("\n---\n\n")
    
    # Original Text
    lines.append("## Original Text\n\n")
    lines.append(f"> {doc.text}\n\n")
    lines.append("---\n\n")
    
    if graph:
        # Hierarchical Structure: Goals → Events → Entities
        lines.append("## Meaning Graph\n\n")
        
        # 1. Goals (Top Level)
        goals = [n for n in graph.nodes if n.type == "Goal"]
        if goals:
            lines.append("### 🎯 Goals\n\n")
            for goal in goals:
                lines.append(f"**{goal.label}**\n")
                lines.append(f"- ID: `{goal.id}`\n")
                
                # Find events linked to this goal
                goal_events = []
                for edge in graph.edges:
                    if edge.source == goal.id or edge.target == goal.id:
                        # Find the connected node
                        connected_id = edge.target if edge.source == goal.id else edge.source
                        connected_node = next((n for n in graph.nodes if n.id == connected_id), None)
                        if connected_node and connected_node.type == "Event":
                            goal_events.append((edge.role, connected_node))
                
                if goal_events:
                    lines.append(f"- **Related Events**:\n")
                    for role, event in goal_events:
                        lines.append(f"  - ({role}) → {event.label}\n")
                
                lines.append("\n")
        
        # 2. Events (Mid Level)
        events = [n for n in graph.nodes if n.type == "Event"]
        if events:
            lines.append("### ⚡ Events\n\n")
            for event in events:
                lines.append(f"**{event.label}**\n")
                lines.append(f"- ID: `{event.id}`\n")
                
                # Event properties
                if hasattr(event, 'properties') and event.properties:
                    if event.properties.get('modality'):
                        lines.append(f"- Modality: *{event.properties['modality']}*\n")
                    if event.properties.get('polarity'):
                        lines.append(f"- Polarity: *{event.properties['polarity']}*\n")
                
                # Find entities and relationships
                event_entities = []
                for edge in graph.edges:
                    if edge.source == event.id:
                        target_node = next((n for n in graph.nodes if n.id == edge.target), None)
                        if target_node and target_node.type == "Entity":
                            event_entities.append((edge.role, target_node))
                
                if event_entities:
                    lines.append(f"- **Participants**:\n")
                    for role, entity in event_entities:
                        lines.append(f"  - {role}: {entity.label}\n")
                
                lines.append("\n")
        
        # 3. Entities (Detail Level)
        entities = [n for n in graph.nodes if n.type == "Entity"]
        if entities:
            lines.append("### 👤 Entities\n\n")
            for entity in entities:
                lines.append(f"- **{entity.label}** (`{entity.id}`)")
                
                # Show what events this entity participates in
                participates_in = []
                for edge in graph.edges:
                    if edge.target == entity.id:
                        source_node = next((n for n in graph.nodes if n.id == edge.source), None)
                        if source_node and source_node.type == "Event":
                            participates_in.append((edge.role, source_node))
                
                if participates_in:
                    lines.append(f" - appears in {len(participates_in)} event(s)")
                
                lines.append("\n")
        
        # 4. Claims (if any)
  
        claims = [n for n in graph.nodes if n.type == "Claim"]
        if claims:
            lines.append("### 💭 Claims\n\n")
            for claim in claims:
                lines.append(f"- **{claim.label}** (`{claim.id}`)\n")
        
        # 5. Key Relationships (Sample of important edges)
        lines.append("### 🔗 Key Relationships\n\n")
        
        # Group edges by type
        cause_edges = [e for e in graph.edges if e.role == "Cause"]
        sequence_edges = [e for e in graph.edges if e.role == "Sequence"]
        contrast_edges = [e for e in graph.edges if e.role == "Contrast"]
        
        if cause_edges:
            lines.append("**Causal:**\n")
            for edge in cause_edges[:5]:  # Limit to 5
                source = next((n for n in graph.nodes if n.id == edge.source), None)
                target = next((n for n in graph.nodes if n.id == edge.target), None)
                if source and target:
                    lines.append(f"- {source.label} → causes → {target.label}\n")
        
        if sequence_edges:
            lines.append("\n**Sequential:**\n")
            for edge in sequence_edges[:5]:
                source = next((n for n in graph.nodes if n.id == edge.source), None)
                target = next((n for n in graph.nodes if n.id == edge.target), None)
                if source and target:
                    lines.append(f"- {source.label} → then → {target.label}\n")
        
        if contrast_edges:
            lines.append("\n**Contrasts:**\n")
            for edge in contrast_edges[:5]:
                source = next((n for n in graph.nodes if n.id == edge.source), None)
                target = next((n for n in graph.nodes if n.id == edge.target), None)
                if source and target:
                    lines.append(f"- {source.label} ⚡ contrasts with ⚡ {target.label}\n")
        
        lines.append("\n")
        
        # 6. Diagnostics
        if graph.diagnostics:
            lines.append("### ⚠️ Diagnostics\n\n")
            
            # Group by kind
            warnings = [d for d in graph.diagnostics if d.severity == "warning"]
            errors = [d for d in graph.diagnostics if d.severity == "error"]
            
            if errors:
                lines.append("**Errors:**\n")
                for diag in errors:
                    lines.append(f"- [{diag.kind}] {diag.message}\n")
                lines.append("\n")
            
            if warnings:
                lines.append("**Warnings:**\n")
                for diag in warnings:
                    lines.append(f"- [{diag.kind}] {diag.message}\n")
                lines.append("\n")
    
    markdown_content = "".join(lines)
    
    return {
        "format": "markdown",
        "content": markdown_content,
        "metadata": {
            "session_id": session_id,
            "node_count": len(graph.nodes) if graph else 0,
            "edge_count": len(graph.edges) if graph else 0,
            "export_timestamp": datetime.utcnow().isoformat()
        }
    }
