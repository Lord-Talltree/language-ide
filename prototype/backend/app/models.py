from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

# Enums
class NodeType(str, Enum):
    ENTITY = "Entity"
    EVENT = "Event"
    CLAIM = "Claim"
    CONTEXT_FRAME = "ContextFrame"
    GOAL = "Goal"

class EdgeRole(str, Enum):
    AGENT = "Agent"
    PATIENT = "Patient"
    INSTRUMENT = "Instrument"
    TIME = "Time"
    LOCATION = "Location"
    CAUSE = "Cause"
    SUPPORT = "Support"
    CONTRADICTION = "Contradiction"
    REFERS_TO = "Refers_to"
    THEME = "Theme"
    EXPERIENCER = "Experiencer"
    SEQUENCE = "Sequence"
    CONDITION = "Condition"
    SAME_AS = "SameAs"
    CONTRAST = "Contrast"

class AmbiguityDimension(str, Enum):
    AMB_LEX = "AMB-LEX"
    AMB_SYN = "AMB-SYN"
    AMB_REF = "AMB-REF"
    AMB_SCOPE = "AMB-SCOPE"
    AMB_TIME = "AMB-TIME"
    AMB_MODAL = "AMB-MODAL"
    AMB_PRAG = "AMB-PRAG"
    AMB_FIG = "AMB-FIG"
    AMB_DISCOURSE = "AMB-DISCOURSE"
    AMB_WORLD = "AMB-WORLD"

class DiagnosticKind(str, Enum):
    AMBIGUITY = "Ambiguity"
    CONTRADICTION = "Contradiction"
    VAGUENESS = "Vagueness"
    KNOWLEDGE_GAP = "KnowledgeGap"

class Severity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    ERROR = "Error"

class ProcessingMode(str, Enum):
    MAP = "Map"
    FICTION = "Fiction"
    TRUTH = "Truth"

# Shared Models
class Span(BaseModel):
    start: int
    end: int
    text: str

class Provenance(BaseModel):
    source_doc: Optional[str] = None
    sentence_index: Optional[int] = None
    span: Optional[Span] = None
    engine_id: str
    engine_version: str
    confidence: float = 1.0
    receipts: List[Dict[str, Any]] = []

# Graph Components
class Node(BaseModel):
    id: str
    type: NodeType
    label: str
    span: Optional[Span] = None
    properties: Dict[str, Any] = {}

class Edge(BaseModel):
    source: str
    target: str
    role: EdgeRole
    provenance: Optional[List[Provenance]] = None

class AmbiguityAlternative(BaseModel):
    label: str
    weight: float
    delta: Dict[str, Any]  # Graph delta

class AmbiguitySet(BaseModel):
    id: str
    dimension: AmbiguityDimension
    alternatives: List[AmbiguityAlternative]
    provenance: Optional[List[Provenance]] = None

class ContextFrame(BaseModel):
    frame_id: str
    frame_type: str  # RealWorld, Fiction, etc.
    speaker_id: Optional[str] = None
    time_anchor: Optional[str] = None
    source_doc: Optional[str] = None
    modality_hint: Optional[str] = None
    local_definitions: Dict[str, Any] = {}

class Diagnostic(BaseModel):
    kind: DiagnosticKind
    severity: Severity
    message: str
    provenance: Optional[List[Provenance]] = None

class MeaningGraph(BaseModel):
    nodes: List[Node] = []
    edges: List[Edge] = []
    ambiguity_sets: List[AmbiguitySet] = []
    context_frames: List[ContextFrame] = []
    diagnostics: List[Diagnostic] = []
    provenance: List[Provenance] = []
    assertions: List['Assertion'] = []

class Assertion(BaseModel):
    subject: str
    predicate: str
    object: Optional[str] = None
    modality: Optional[str] = None  # e.g., "must", "might"
    condition: Optional[str] = None # e.g., "if X"
    source_event_id: str
    confidence: float = 1.0

# API Models
class CreateDocRequest(BaseModel):
    text: str
    lang: str = "en"
    id: Optional[str] = None

class AnalyzeOptions(BaseModel):
    stages: List[str] = ["segment", "parse", "graph"]
    detail: str = "full"
    maxDiagnostics: int = 50
    processing_mode: ProcessingMode = ProcessingMode.MAP
    schemaSet: Optional[str] = None
    privacy: Dict[str, bool] = {"store": True}

class AnalyzeRequest(BaseModel):
    docId: str
    options: Optional[AnalyzeOptions] = None

class DocResponse(BaseModel):
    id: str
    text: str
    lang: str
    created_at: str

class AnalysisSummary(BaseModel):
    docId: str
    graph_summary: Dict[str, int] # e.g., {"nodes": 10, "edges": 15}
    top_diagnostics: List[Diagnostic]
