# L-ide CLI Tool

Command-line interface for L-ide - attach to any AI conversation.

## Installation

### Local Development
```bash
# Make executable
chmod +x cli/lide.py

# Create symlink (optional)
ln -s $(pwd)/cli/lide.py /usr/local/bin/lide

# Or add to PATH
export PATH="$PATH:$(pwd)/cli"
```

### Requirements
```bash
pip install requests
```

## Usage

### Start Interactive Session
```bash
# New session
lide attach

# Resume existing session
lide attach --session SESSION_ID
```

### List Sessions
```bash
lide list
```

### Export Session
```bash
# Export as Markdown
lide export SESSION_ID

# Export as JSON
lide export SESSION_ID --format json
```

## Features

- **Real-time Analysis**: Messages analyzed as you type
- **Color-coded Diagnostics**: 
  - ❌ Errors (red)
  - ⚠️ Warnings (yellow)
  - ✓ Success (green)
- **Session Management**: Create, resume, and export sessions
- **Markdown/JSON Export**: Full session exports with hierarchy

## Examples

### Basic Usage
```bash
$ lide attach
Created new session: e4b2c...
L-ide is monitoring your conversation

You: I want to build an app
✓ No issues detected

You: The app should be fast and also slow
⚠️  WARNINGS:
  ⚠️  [Contradiction] Conflicting properties: fast vs slow

Graph: 5 nodes, 3 edges
```

### Export Session
```bash
$ lide export e4b2c

# Session Export: e4b2c...

## Metadata
- Session ID: e4b2c...
- Nodes: 5
- Edges: 3
...
```

## Architecture

The CLI tool:
1. **Monitors** user input in terminal
2. **Sends** messages to L-ide backend API
3. **Analyzes** responses for diagnostics
4. **Displays** warnings/errors in real-time
5. **Manages** sessions locally

## Integration

The CLI works with:
- Any AI chat in terminal (ChatGPT code, Claude CLI, etc.)
- Shell scripts
- Automation workflows
- CI/CD pipelines

## Roadmap

- [ ] Clipboard monitoring mode
- [ ] File watching mode
- [ ] Webhook integration
- [ ] Custom diagnostic rules
