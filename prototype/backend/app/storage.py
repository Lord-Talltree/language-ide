"""
Storage abstraction layer for L-ide.

Provides pluggable backend storage for documents, graphs, and sessions.
Default implementation uses SQLite for local-first persistence.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from app.models import MeaningGraph, DocResponse
from datetime import datetime


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save_document(self, doc_id: str, text: str, lang: str) -> DocResponse:
        """Save a document and return metadata."""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[DocResponse]:
        """Retrieve document metadata by ID."""
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document and its associated graph. Returns True if found."""
        pass
    
    @abstractmethod
    def save_graph(self, doc_id: str, graph: MeaningGraph) -> None:
        """Save a meaning graph for a document."""
        pass
    
    @abstractmethod
    def get_graph(self, doc_id: str) -> Optional[MeaningGraph]:
        """Retrieve a meaning graph by document ID."""
        pass
    
    @abstractmethod
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[DocResponse]:
        """List all documents with pagination."""
        pass


class InMemoryStorage(StorageBackend):
    """
    Simple in-memory storage (original implementation).
    Data is lost on restart. Useful for testing.
    """
    
    def __init__(self):
        self.docs: Dict[str, Dict] = {}
        self.graphs: Dict[str, Dict] = {}
    
    def save_document(self, doc_id: str, text: str, lang: str) -> DocResponse:
        doc = {
            "id": doc_id,
            "text": text,
            "lang": lang,
            "created_at": datetime.utcnow().isoformat()
        }
        self.docs[doc_id] = doc
        return DocResponse(**doc)
    
    def get_document(self, doc_id: str) -> Optional[DocResponse]:
        doc = self.docs.get(doc_id)
        return DocResponse(**doc) if doc else None
    
    def delete_document(self, doc_id: str) -> bool:
        existed = doc_id in self.docs
        self.docs.pop(doc_id, None)
        self.graphs.pop(doc_id, None)
        return existed
    
    def save_graph(self, doc_id: str, graph: MeaningGraph) -> None:
        self.graphs[doc_id] = graph.dict()
    
    def get_graph(self, doc_id: str) -> Optional[MeaningGraph]:
        graph_dict = self.graphs.get(doc_id)
        return MeaningGraph(**graph_dict) if graph_dict else None
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[DocResponse]:
        all_docs = list(self.docs.values())
        paginated = all_docs[offset:offset + limit]
        return [DocResponse(**doc) for doc in paginated]


class SQLiteStorage(StorageBackend):
    """
    SQLite-based persistent storage.
    Stores documents and graphs locally in a single .db file.
    """
    
    def __init__(self, db_path: str = "lide.db"):
        import sqlite3
        import json
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return dict-like rows
        self._init_schema()
    
    def _init_schema(self):
        """Create tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                text TEXT NOT NULL,
                lang TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Graphs table (stores JSON blob)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS graphs (
                doc_id TEXT PRIMARY KEY,
                graph_json TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def save_document(self, doc_id: str, text: str, lang: str) -> DocResponse:
        import json
        
        created_at = datetime.utcnow().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO documents (id, text, lang, created_at)
            VALUES (?, ?, ?, ?)
        """, (doc_id, text, lang, created_at))
        self.conn.commit()
        
        return DocResponse(id=doc_id, text=text, lang=lang, created_at=created_at)
    
    def get_document(self, doc_id: str) -> Optional[DocResponse]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        
        if row:
            return DocResponse(
                id=row["id"],
                text=row["text"],
                lang=row["lang"],
                created_at=row["created_at"]
            )
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        deleted = cursor.rowcount > 0
        self.conn.commit()
        return deleted
    
    def save_graph(self, doc_id: str, graph: MeaningGraph) -> None:
        import json
        
        graph_json = json.dumps(graph.dict())
        updated_at = datetime.utcnow().isoformat()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO graphs (doc_id, graph_json, updated_at)
            VALUES (?, ?, ?)
        """, (doc_id, graph_json, updated_at))
        self.conn.commit()
    
    def get_graph(self, doc_id: str) -> Optional[MeaningGraph]:
        import json
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT graph_json FROM graphs WHERE doc_id = ?", (doc_id,))
        row = cursor.fetchone()
        
        if row:
            graph_dict = json.loads(row["graph_json"])
            return MeaningGraph(**graph_dict)
        return None
    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[DocResponse]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM documents
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        return [DocResponse(
            id=row["id"],
            text=row["text"],
            lang=row["lang"],
            created_at=row["created_at"]
        ) for row in rows]
    
    def close(self):
        """Close the database connection."""
        self.conn.close()


# Singleton storage instance
_storage_instance: Optional[StorageBackend] = None


def get_storage(backend: str = "sqlite", **kwargs) -> StorageBackend:
    """
    Get the storage backend instance.
    
    Args:
        backend: "memory" or "sqlite" (default: "sqlite")
        **kwargs: Additional args passed to backend constructor
    
    Returns:
        StorageBackend instance
    """
    global _storage_instance
    
    if _storage_instance is None:
        if backend == "memory":
            _storage_instance = InMemoryStorage()
        elif backend == "sqlite":
            db_path = kwargs.get("db_path", "lide.db")
            _storage_instance = SQLiteStorage(db_path=db_path)
        else:
            raise ValueError(f"Unknown backend: {backend}")
    
    return _storage_instance
