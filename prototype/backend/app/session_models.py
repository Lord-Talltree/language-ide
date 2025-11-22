"""
Session management models.
Extends the storage layer with session-specific functionality.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SessionMetadata(BaseModel):
    """Metadata for a session (document + graph)."""
    id: str
    name: str  # User-friendly name
    created_at: str
    updated_at: str
    node_count: int = 0
    edge_count: int = 0
    diagnostic_count: int = 0


class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    name: Optional[str] = None
    text: Optional[str] = ""
    lang: str = "en"


class UpdateSessionRequest(BaseModel):
    """Request to update session metadata."""
    name: Optional[str] = None


class ExportFormat(BaseModel):
    """Export format options."""
    format: str = "json"  # "json" or "markdown"
