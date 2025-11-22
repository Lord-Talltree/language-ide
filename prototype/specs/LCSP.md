# Language Comprehension Server Protocol (LCSP) v0.1

## Overview
LCSP defines a standard HTTP/WebSocket API for systems that map natural language to structured meaning representations.

## Endpoints

### System Info
- `GET /v0/health`: System health status.
- `GET /v0/models`: List available models/plugins.
- `GET /v0/capabilities`: Server capabilities (streaming, store, etc.).

### Document Management
- `POST /v0/docs`: Create or update a document.
  - Body: `{"text": "...", "lang": "en", "id": "optional-uuid"}`
- `GET /v0/docs/{id}`: Retrieve document metadata.
- `DELETE /v0/docs/{id}`: Delete a document.

### Analysis
- `POST /v0/analyze`: Trigger analysis pipeline.
  - Body:
    ```json
    {
      "docId": "uuid",
      "options": {
        "stages": ["segment", "parse", "graph"],
        "detail": "full",
        "processing_mode": "Map",
        "privacy": { "store": false }
      }
    }
    ```
- `GET /v0/docs/{id}/graph`: Retrieve the Meaning Graph.
- `GET /v0/docs/{id}/diagnostics`: Retrieve diagnostics.
- `WS /v0/stream/analyze?docId=...`: WebSocket for streaming incremental updates.

### Feedback
- `POST /v0/feedback`: Submit user feedback on analysis results.

## Data Models
See `meaning_graph.schema.json` for the full graph structure.
