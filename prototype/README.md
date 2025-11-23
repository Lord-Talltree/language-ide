# L-ide: A GPS Protocol for AI Conversations

**Local-first, protocol-based system for mapping AI conversations into queryable Meaning Graphs.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## What is L-ide?

L-ide is a **protocol, not just a product**. It sits alongside AI conversations (ChatGPT, Claude, local models) and automatically builds a structured Meaning Graph showing:
- **What was discussed** (Goals, Events, Entities)
- **How it connects** (Relationships, Dependencies)  
- **What's unclear** (Ambiguities, Contradictions)

Think "Git for AI conversations" - it tracks context so you and the AI never lose the big picture.

## Quick Start

### Prerequisites
- Docker & Docker Compose
- 4GB RAM minimum

### One-Click Deployment
```bash
git clone https://github.com/Lord-Talltree/language-ide.git
cd language-ide/prototype
docker compose up -d
```

**Access the system:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Backend API: http://localhost:8000

**Stop services:**
```bash
docker compose down
```

## Features

### Core Capabilities
- ✅ **Meaning Graph Extraction** - Automatic NLP parsing (spaCy)
- ✅ **Session Management** - Save/load/export multiple sessions
- ✅ **SQLite Persistence** - Data survives restarts
- ✅ **JSON/Markdown Export** - Portable session backups
- ✅ **Real-time Analysis** - Process text as you chat
- ✅ **Diagnostic System** - Detect contradictions, ambiguities

### Advanced Features
- **Continuity Checking** - Flags contradictions across messages
- **Ambiguity Detection** - Identifies vague pronouns and references
- **Discourse Analysis** - Extracts cause/contrast/sequence relationships
- **Identity Resolution** - Links pronouns to entities (SAME_AS edges)
- **Context Frames** - Separate RealWorld vs Fiction vs Hypothetical
- **Plugin Architecture** - Extendable checker system

## API Overview

### Session Management
```bash
# Create session
curl -X POST http://localhost:8000/v0/sessions \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to build an app", "lang": "en"}'

# List sessions
curl http://localhost:8000/v0/sessions

# Export to Markdown
curl "http://localhost:8000/v0/sessions/{id}/export?format=markdown"
```

### Analysis
```bash
# Create document
curl -X POST http://localhost:8000/v0/docs \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here", "id": "doc-1"}'

# Analyze document
curl -X POST http://localhost:8000/v0/analyze \
  -H "Content-Type: application/json" \
  -d '{"docId": "doc-1", "options": {"processing_mode": "Map"}}'

# Get graph
curl http://localhost:8000/v0/docs/doc-1/graph
```

## Architecture

```
User Input → [L-ide Backend]
              ↓
          NLP Pipeline (spaCy)
              ↓
        Graph Construction
              ↓
       Checker Plugins
              ↓
         SQLite Storage
              ↓
      REST API / WebSocket
              ↓
        [Frontend Dashboard]
```

### Directory Structure
```
prototype/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api.py           # REST endpoints
│   │   ├── session_api.py   # Session management
│   │   ├── storage.py       # SQLite persistence
│   │   ├── pipeline.py      # NLP processing
│   │   ├── checkers/        # Plugin implementations
│   │   └── models.py        # Pydantic models
│   ├── tests/        # Integration tests
│   └── main.py       # FastAPI entry point
├── frontend/         # React + TypeScript UI
├── DEPLOYMENT.md     # Production deployment guide
└── docker-compose.yml
```

## Development

### Run Tests
```bash
cd prototype/backend
pytest -v
```

### Local Development (without Docker)
```bash
# Backend
cd prototype/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend  
cd prototype/frontend
npm install
npm run dev
```

## Data Persistence

Sessions are stored in SQLite:
- **Location**: `prototype/backend/lide.db` (local) or `/app/data/lide.db` (Docker)
- **Backup**: `docker compose exec backend cat /app/data/lide.db > backup.db`
- **Reset**: `docker compose down -v` (WARNING: deletes all data)

## Monetization & Licensing

L-ide uses **dual licensing**:

- **Core Protocol** (MIT): Free, open source
  - Graph schema, API, storage layer
- **Pro Checkers** (Proprietary): Paid ($49 one-time)
  - Advanced continuity checking
  - Enhanced ambiguity detection
  - Custom policy checkers

See [LICENSE](LICENSE) and [PROPRIETARY_LICENSE.md](prototype/backend/app/checkers/PROPRIETARY_LICENSE.md)

## Documentation

- [Deployment Guide](prototype/DEPLOYMENT.md) - Production setup
- [Architecture](prototype/ARCHITECTURE.md) - System design
- [Usage Guide](prototype/USAGE.md) - API examples
- [Defensive Publication](https://lord-talltree.github.io/language-ide/) - Technical spec

## Roadmap

**Week 1** (✅ COMPLETE):
- SQLite persistence
- Session management
- Docker deployment

**Week 2** (In Progress):
- Hierarchy visualization
- Export/import features
- Dashboard improvements

**Week 3**:
- CLI tool (`lide attach`)
- Chrome extension

**Week 4**:
- Launch on Hacker News
- Payment integration (Gumroad)

## Contributing

Contributions welcome! This is an open protocol - build clients, add checkers, improve the core.

1. Fork the repo
2. Create a feature branch
3. Submit a pull request

## Support

- **GitHub Issues**: https://github.com/Lord-Talltree/language-ide/issues
- **Technical Spec**: https://lord-talltree.github.io/language-ide/

## License

Dual-licensed: MIT (protocol) + Proprietary (Pro checkers). See [LICENSE](LICENSE).

---

**Built by**: Ruben Kai Baden  
**Published**: November 22, 2025
