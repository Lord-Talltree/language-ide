# System Architecture

## Overview

Language IDE is designed as a modular, pipeline-based system. It separates the core "mapping" of language from the "evaluation" or "interpretation" of that meaning.

## Components

### 1. Backend (FastAPI)
- **API Layer**: Exposes REST endpoints for document management and analysis.
- **Pipeline**: Orchestrates the NLP tasks.
    - **SpaCy**: Used for tokenization, POS tagging, dependency parsing, and NER.
    - **Graph Builder**: Converts NLP output into the `MeaningGraph` structure.
    - **Ambiguity Manager**: Detects and annotates ambiguities (AmbiguitySets).
- **Interpreters**: Abstraction layer for post-processing the graph.
    - `MapInterpreter`: Baseline.
    - `FictionInterpreter`: Context-aware filtering.
    - `TruthInterpreter`: Plugin orchestrator.
- **Plugin System**: Registry and contract for external engines.

### 2. Frontend (React)
- **Graph Visualization**: Uses Cytoscape.js to render the Meaning Graph.
- **Diagnostics Panel**: Displays issues found by the pipeline and plugins.
- **API Client**: Communicates with the backend.

## Data Flow

1.  **Ingestion**: User submits text -> Document created.
2.  **Analysis Request**: User requests analysis with specific options (Mode).
3.  **Pipeline Execution**:
    - Text -> NLP (Tokens, Deps, Ents) -> Nodes/Edges.
    - Ambiguity Detection -> AmbiguitySets.
    - Context Frame creation.
4.  **Interpretation**:
    - The selected `Interpreter` processes the raw graph.
    - If `Truth` mode, plugins are executed.
    - Plugins return diagnostics and graph updates.
5.  **Response**: Final `MeaningGraph` returned to client.

## Data Model

The **Meaning Graph** is the central data structure, defined in `specs/meaning_graph.schema.json`.
- **Nodes**: Entities, Events, Claims.
- **Edges**: Semantic roles (Agent, Patient, Cause, etc.).
- **AmbiguitySets**: Alternative interpretations.
- **ContextFrames**: Scoping for claims (RealWorld vs Fiction).

## Performance & Scalability

- **Incremental Processing**: The pipeline is designed to be modular. Future versions can support streaming updates via WebSocket.
- **Lazy Evaluation**: Plugins are only run when requested (Truth mode).
