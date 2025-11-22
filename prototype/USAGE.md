# Usage Guide

## API Interaction

### Create a Document
```bash
curl -X POST http://localhost:8000/v0/docs \
  -H "Content-Type: application/json" \
  -d '{"text": "Gregor Samsa awoke from uneasy dreams.", "lang": "en"}'
```

### Analyze a Document
```bash
curl -X POST http://localhost:8000/v0/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "docId": "<DOC_ID>",
    "options": {
      "processing_mode": "Map",
      "stages": ["segment", "parse", "graph"],
      "detail": "full"
    }
  }'
```

### Fetch the Graph
```bash
curl http://localhost:8000/v0/docs/<DOC_ID>/graph
```

## Switching Interpreters

The system supports different "Interpreters" that change how the graph is processed and how diagnostics are reported.

- **Map** (Default): Faithful mapping of text to graph. Contradictions are warnings.
- **Fiction**: Downgrades world-knowledge contradictions to "Narrative" info. Useful for stories.
- **Truth**: Runs registered validation plugins (e.g., Truth Checker) to flag implausible claims.

To switch, set `processing_mode` in the `/analyze` request:
```json
"options": {
  "processing_mode": "Truth"
}
```

## Developing Plugins

Plugins allow you to extend the analysis capabilities.

1.  Create a new class inheriting from `Plugin` in `backend/app/plugins.py`.
2.  Implement the `run(graph, context)` method.
3.  Return a dictionary with `diagnostics`, `knowledge_validations`, or `graph_updates`.
4.  Register the plugin in `backend/app/api.py` (or a config file).

Example:
```python
class MyPlugin(Plugin):
    def run(self, graph, context):
        return {"diagnostics": []}
```

## Privacy

To run in no-store mode (not yet fully implemented in prototype storage), set:
```json
"privacy": { "store": false }
```
## The Logic Layer (New)
L-ide now extracts atomic **Assertions** from the graph to enable automated reasoning.

### Assertions
The `graph` object now includes an `assertions` list:
```json
"assertions": [
  {
    "subject": "server",
    "predicate": "be",
    "object": "live",
    "condition": null
  },
  {
    "subject": "server",
    "predicate": "be",
    "object": "down",
    "condition": null
  }
]
```

### Logic Checks
You can use these assertions to detect:
1.  **Contradictions:** When two assertions claim conflicting states for the same subject.
2.  **Open Questions:** When an assertion is conditional (e.g., "If X, then Y"), it represents an unverified assumption.

## Identity Resolution (New)
L-ide automatically links pronouns to their referents to create a unified graph.
*   **Edges:** `SAME_AS` edges connect nodes like `he` -> `Gregor`.
*   **Visualization:** These appear as subtle, transparent lines in the graph view, allowing you to see the "web of identity" without cluttering the action.

## Timeline Visualization (New)
Switch the Graph View to **Timeline Mode** to see the narrative unfold from left to right.
*   **X-Axis:** Represents time/order of appearance in the text.
*   **Structure:** Events form a central spine, with participating entities floating around them, making it easy to trace cause and effect.
