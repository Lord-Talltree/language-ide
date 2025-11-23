"""
Integration tests for session management API endpoints.
Tests the full CRUD workflow with SQLite persistence.
"""

import pytest
from fastapi.testclient import TestClient
import os
import tempfile


@pytest.fixture
def client():
    """Create a test client with temporary database."""
    # Use temporary database for tests
    test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    os.environ['DATABASE_PATH'] = test_db.name
    
    # Clear singleton to force new instance with test DB
    import app.storage
    app.storage._storage_instance = None
    
    # Import app after setting env var
    from main import app as fastapi_app
    client = TestClient(fastapi_app)
    yield client
    
    # Cleanup
    os.unlink(test_db.name)
    app.storage._storage_instance = None


def test_create_session(client):
    """Test creating a new session."""
    response = client.post("/v0/sessions", json={
        "text": "Hello, this is a test session",
        "name": "Test Session",
        "lang": "en"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["name"] == data["id"]  # MVP: name = id
    assert data["node_count"] == 0  # No analysis yet
    assert data["edge_count"] == 0
    

def test_list_sessions(client):
    """Test listing all sessions."""
    # Create two sessions
    client.post("/v0/sessions", json={"text": "Session 1"})
    client.post("/v0/sessions", json={"text": "Session 2"})
    
    response = client.get("/v0/sessions")
    assert response.status_code == 200
    
    sessions = response.json()
    assert len(sessions) == 2


def test_get_session(client):
    """Test retrieving a specific session."""
    # Create session
    create_resp = client.post("/v0/sessions", json={"text": "Test"})
    session_id = create_resp.json()["id"]
    
    # Get session
    response = client.get(f"/v0/sessions/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == session_id


def test_get_nonexistent_session(client):
    """Test 404 for nonexistent session."""
    response = client.get("/v0/sessions/fake-id-12345")
    assert response.status_code == 404


def test_delete_session(client):
    """Test deleting a session."""
    # Create session
    create_resp = client.post("/v0/sessions", json={"text": "Delete me"})
    session_id = create_resp.json()["id"]
    
    # Delete session
    response = client.delete(f"/v0/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    
    # Verify it's gone
    get_resp = client.get(f"/v0/sessions/{session_id}")
    assert get_resp.status_code == 404


def test_session_with_graph(client):
    """Test session metadata includes graph stats after analysis."""
    # Create document
    doc_resp = client.post("/v0/docs", json={
        "text": "I want to build a system. The system should be fast.",
        "lang": "en"
    })
    doc_id = doc_resp.json()["id"]
    
    # Analyze to create graph
    client.post("/v0/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map"}
    })
    
    # Get session metadata
    response = client.get(f"/v0/sessions/{doc_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["node_count"] > 0  # Should have nodes from analysis
    assert data["edge_count"] >= 0


def test_export_json(client):
    """Test JSON export."""
    # Create session
    create_resp = client.post("/v0/sessions", json={
        "text": "Export test"
    })
    session_id = create_resp.json()["id"]
    
    # Export as JSON
    response = client.get(f"/v0/sessions/{session_id}/export?format=json")
    assert response.status_code == 200
    
    data = response.json()
    assert "session_id" in data
    assert data["session_id"] == session_id
    assert "document" in data
    assert "graph" in data


def test_export_markdown(client):
    """Test Markdown export."""
    # Create and analyze session
    doc_resp = client.post("/v0/docs", json={
        "text": "I want to learn Python. Python is a programming language.",
        "lang": "en"
    })
    doc_id = doc_resp.json()["id"]
    
    client.post("/v0/analyze", json={
        "docId": doc_id,
        "options": {"processing_mode": "Map"}
    })
    
    # Export as Markdown
    response = client.get(f"/v0/sessions/{doc_id}/export?format=markdown")
    assert response.status_code == 200
    
    data = response.json()
    assert data["format"] == "markdown"
    assert "content" in data
    assert "# Session:" in data["content"]
    assert "## Original Text" in data["content"]


def test_persistence_across_requests(client):
    """Test that data persists in SQLite between requests."""
    # Create session
    create_resp = client.post("/v0/sessions", json={"text": "Persist me"})
    session_id = create_resp.json()["id"]
    
    # Make multiple requests - data should persist
    for _ in range(3):
        response = client.get(f"/v0/sessions/{session_id}")
        assert response.status_code == 200
        assert response.json()["id"] == session_id


def test_invalid_export_format(client):
    """Test error handling for invalid export format."""
    create_resp = client.post("/v0/sessions", json={"text": "Test"})
    session_id = create_resp.json()["id"]
    
    response = client.get(f"/v0/sessions/{session_id}/export?format=xml")
    assert response.status_code == 400
