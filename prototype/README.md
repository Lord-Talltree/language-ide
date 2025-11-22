# Language IDE

**Map-first, Plugin-Engines, Portable**

Language IDE is an autonomous software system that maps natural language into a structured **Meaning Graph** (events, entities, claims, contexts, ambiguity) and exposes an engine/plugin architecture for optional validators (truth-checkers, plausibility models, discourse analyzers).

## Core Philosophy

1.  **Map-first**: Default behavior maps language to graph. Contradictions are annotations, not errors.
2.  **Event-centric**: Core model is event-centric with explicit role edges.
3.  **ContextFrame**: Every claim attaches to a ContextFrame (RealWorld, Fiction, etc.).
4.  **AmbiguitySets**: Ambiguities are preserved as first-class objects with alternatives.

## Quickstart

### Prerequisites
- Docker & Docker Compose

### Running Locally

1.  Clone the repository.
2.  Start the system:
    ```bash
    docker-compose up --build
    ```
3.  Access the Frontend: [http://localhost:3000](http://localhost:3000)
4.  Access the API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project Structure

- `backend/`: FastAPI application (Python)
- `frontend/`: React + TypeScript application
- `specs/`: Documentation and Schemas (`LCSP.md`, `meaning_graph.schema.json`)
- `plugins/`: Plugin implementations
- `data/`: Sample data and golden sets

## Features

- **Meaning Graph Generation**: Extracts entities, events, and relations.
- **Ambiguity Detection**: Identifies vague terms and figurative language.
- **Interpreters**:
    - **Map**: Pure mapping.
    - **Logic Layer**: Extracts atomic assertions and detects contradictions (e.g. "Server is live" vs "Server is down").
- **Identity Resolution**: Links pronouns ("he", "it") to their entities ("Gregor", "Server") using `SAME_AS` edges.
- **Timeline Visualization**: Organizes the graph chronologically, showing the flow of events and entity interactions over time.
- **Plugin Architecture**: Extendable for Truth Checking, Discourse Analysis, and more.

## Documentation

- [Usage Guide](USAGE.md)
- [Architecture](ARCHITECTURE.md)
- [API Specification](specs/LCSP.md)
