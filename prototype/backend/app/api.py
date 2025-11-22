from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime

from app.models import (
    CreateDocRequest, DocResponse, AnalyzeRequest, AnalysisSummary, MeaningGraph
)
from pydantic import BaseModel

router = APIRouter()

# Storage backend (persistent SQLite)
from app.storage import get_storage
storage = get_storage(backend="sqlite", db_path="lide.db")

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

@router.get("/models")
async def list_models():
    return {
        "models": [
            {"id": "spacy-en-core-web-sm", "type": "nlp", "version": "3.6.0"},
            {"id": "map-interpreter", "type": "interpreter", "version": "0.1.0"}
        ]
    }

@router.get("/capabilities")
async def capabilities():
    return {
        "streaming": True,
        "store": True,
        "modes": ["Map", "Fiction", "Truth"]
    }

# Register Plugins (Prototype)
from app.plugins import registry
from plugins.truth_checker import TruthCheckerPlugin
from plugins.discourse import DiscoursePlugin
registry.register(TruthCheckerPlugin())
registry.register(DiscoursePlugin())

@router.post("/docs", response_model=DocResponse)
async def create_doc(request: CreateDocRequest):
    doc_id = request.id or str(uuid.uuid4())
    return storage.save_document(doc_id, request.text, request.lang)

@router.get("/docs/{doc_id}", response_model=DocResponse)
async def get_doc(doc_id: str):
    doc = storage.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/docs/{doc_id}")
async def delete_doc(doc_id: str):
    deleted = storage.delete_document(doc_id)
    return {"status": "deleted" if deleted else "not_found"}

@router.post("/analyze", response_model=AnalysisSummary)
async def analyze_doc(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    doc = storage.get_document(request.docId)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    try:
        from app.pipeline import get_pipeline
        pipeline = get_pipeline()
        
        # Run pipeline (synchronously for now for simplicity, can be backgrounded)
        graph = pipeline.process(doc["text"], request.docId)
        
        # Apply Interpreter
        from app.interpreters import get_interpreter
        from app.models import AnalyzeOptions
        options = request.options or AnalyzeOptions()
        interpreter = get_interpreter(options.processing_mode)
        graph = interpreter.interpret(graph)
        
        storage.save_graph(request.docId, graph)
        
        return AnalysisSummary(
            docId=request.docId,
            graph_summary={"nodes": len(graph.nodes), "edges": len(graph.edges)},
            top_diagnostics=graph.diagnostics[:5]
        )
    except Exception as e:
        import traceback
        error_detail = f"Error during analysis: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/docs/{doc_id}/graph", response_model=MeaningGraph)
async def get_graph(doc_id: str):
    graph = storage.get_graph(doc_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found. Run /analyze first.")
    return graph

@router.get("/docs/{doc_id}/logic")
async def get_logic(doc_id: str):
    graph = storage.get_graph(doc_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found. Run /analyze first.")
    
    graph_data = graph.dict()
    # Reconstruct objects
    from app.models import MeaningGraph, Assertion
    assertions = [Assertion(**a) for a in graph_data.get('assertions', [])]
    # We need a proper MeaningGraph object for LogicEngine, but it only uses assertions for now.
    # But let's be safe and reconstruct minimal graph.
    graph = MeaningGraph(
        nodes=[], 
        edges=[], 
        assertions=assertions,
        ambiguity_sets=[],
        context_frames=[],
        diagnostics=[],
        provenance=[]
    )
    
    from app.logic import LogicEngine
    engine = LogicEngine(graph)
    
    return {
        "contradictions": engine.find_contradictions(),
        "open_questions": engine.find_open_questions()
    }

# --- Dashboard Endpoints ---

from app.agent.session import get_session
from app.agent.interceptor import Interceptor

class ChatMessage(BaseModel):
    message: str

@router.get("/session")
async def get_session_state():
    """Returns the current session graph and history."""
    session = get_session()
    return {
        "graph": session.get_graph(),
        "history": session.history
    }

@router.post("/chat/message")
async def chat_message(msg: ChatMessage):
    """
    Processes a user message via the Interceptor.
    Returns the system warning (if any) and a simulated agent response.
    """
    session = get_session()
    interceptor = Interceptor()
    
    # Run Interceptor
    warning = interceptor.check_and_inject(msg.message, session)
    
    # Simulate Agent Response
    if warning:
        agent_response = f"Wait, I'm confused. {warning.replace('[SYSTEM WARNING: ', '').replace(']', '')}"
    else:
        agent_response = "I understand. (No issues detected)"
        
    return {
        "response": agent_response,
        "warning": warning
    }
