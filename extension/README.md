# L-ide Chrome Extension

Monitor AI conversations for contradictions, ambiguities, and context issues.

## Features

- **Real-time Monitoring**: Automatically analyzes messages as you chat
- **Inline Warnings**: Displays diagnostics directly in ChatGPT/Claude interface
- **Session Management**: Creates and tracks conversation sessions
- **Export**: Download session analysis as Markdown

## Installation

### Load Unpacked Extension (Development)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `extension/` directory

### Prerequisites

**L-ide backend must be running:**
```bash
cd prototype/backend
uvicorn main:app --reload
```

Backend will run at `http://localhost:8000`

## Usage

### 1. Start Monitoring

1. Navigate to ChatGPT or Claude
2. Click the L-ide extension icon
3. Click "Start Monitoring"
4. A new session will be created

### 2. Chat Normally

Type your messages in ChatGPT/Claude as usual. L-ide will:
- Analyze each message
- Detect contradictions and ambiguities
- Display warnings inline

### 3. View Diagnostics

Warnings appear below your messages:

```
⚠️ L-ide Detected Issues:
❌ Contradiction: "fast" conflicts with "slow"
⚠️ Ambiguity: Unclear reference to "it"
```

### 4. Export Session

Click "Export Session" in the popup to download your conversation analysis as Markdown.

## Supported Platforms

- ✅ ChatGPT (chat.openai.com)
- ✅ Claude (claude.ai)
- 🔄 More coming soon

## How It Works

1. **Content Script** monitors chat interface for new messages
2. **API Calls** send messages to L-ide backend for analysis
3. **Diagnostics** are displayed inline with visual styling
4. **Sessions** track conversation history and graph state

## Architecture

```
ChatGPT/Claude UI
    ↓
Content Script (content.js)
    ↓
L-ide Backend API
    ↓
Analysis + Graph Building
    ↓
Diagnostics returned
    ↓
Inline warnings displayed
```

## Configuration

Edit `content.js` to change API endpoint:
```javascript
const API_BASE = 'http://localhost:8000/v0';
```

## Troubleshooting

### "Backend not running"
Start the backend:
```bash
cd prototype/backend
uvicorn main:app --reload
```

### Warnings not appearing
1. Check browser console for errors (F12)
2. Verify backend is accessible at http://localhost:8000
3. Reload the page after enabling monitoring

### Extension not loading
1. Enable Developer mode in chrome://extensions/
2. Check manifest.json for syntax errors
3. Reload extension after code changes

## Privacy

- All processing happens locally
- Messages sent to `localhost:8000` only
- No data leaves your machine
- Sessions stored in local SQLite database

## Development

### File Structure
```
extension/
├── manifest.json       # Extension configuration
├── background.js       # Service worker
├── content.js          # ChatGPT/Claude monitoring
├── content.css         # Warning styles
├── popup.html          # Popup UI
├── popup.js            # Popup logic
└── icons/              # Extension icons
```

### Testing

1. Make changes to extension files
2. Go to `chrome://extensions/`
3. Click reload icon for L-ide extension
4. Refresh ChatGPT/Claude page
5. Test functionality

## Roadmap

- [ ] Manifest V3 optimizations
- [ ] Offline mode with queue
- [ ] Custom diagnostic rules
- [ ] Multi-session management
- [ ] Firefox support
