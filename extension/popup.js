/**
 * L-ide Chrome Extension - Popup Script
 */

const API_BASE = 'http://localhost:8000/v0';

let isMonitoring = false;
let currentSessionId = null;

// DOM elements
const loadingDiv = document.getElementById('loading');
const contentDiv = document.getElementById('content');
const statusDiv = document.getElementById('status');
const sessionInfoDiv = document.getElementById('session-info');
const sessionIdSpan = document.getElementById('session-id');
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const exportBtn = document.getElementById('export-btn');

// Initialize
async function init() {
    // Load saved state
    const result = await chrome.storage.local.get(['monitoring', 'sessionId']);
    isMonitoring = result.monitoring || false;
    currentSessionId = result.sessionId || null;

    // Check if backend is running
    const backendRunning = await checkBackend();

    if (!backendRunning) {
        showError('Backend not running. Start it at http://localhost:8000');
        return;
    }

    updateUI();
    loadingDiv.style.display = 'none';
    contentDiv.style.display = 'block';
}

async function checkBackend() {
    try {
        const response = await fetch(`${API_BASE}/health`, { method: 'GET' });
        return response.ok;
    } catch (e) {
        return false;
    }
}

function showError(message) {
    loadingDiv.innerHTML = `<div style="color: #ef4444;">${message}</div>`;
}

async function startMonitoring() {
    try {
        // Create new session
        const response = await fetch(`${API_BASE}/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: '', lang: 'en' })
        });
        const session = await response.json();
        currentSessionId = session.id;

        // Save state
        await chrome.storage.local.set({
            monitoring: true,
            sessionId: currentSessionId
        });

        // Notify content script
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        await chrome.tabs.sendMessage(tab.id, {
            action: 'start_monitoring',
            sessionId: currentSessionId
        });

        isMonitoring = true;
        updateUI();
    } catch (error) {
        console.error('Failed to start monitoring:', error);
        alert('Failed to start monitoring. Is the backend running?');
    }
}

async function stopMonitoring() {
    // Save state
    await chrome.storage.local.set({ monitoring: false });

    // Notify content script
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    await chrome.tabs.sendMessage(tab.id, { action: 'stop_monitoring' });

    isMonitoring = false;
    updateUI();
}

async function exportSession() {
    if (!currentSessionId) return;

    try {
        const response = await fetch(
            `${API_BASE}/sessions/${currentSessionId}/export?format=markdown`
        );
        const data = await response.json();

        // Download as file
        const blob = new Blob([data.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lide-session-${currentSessionId.substring(0, 8)}.md`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Failed to export:', error);
        alert('Failed to export session');
    }
}

function updateUI() {
    if (isMonitoring) {
        statusDiv.className = 'status active';
        statusDiv.textContent = '✅ Monitoring active';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        exportBtn.style.display = 'block';

        if (currentSessionId) {
            sessionInfoDiv.style.display = 'block';
            sessionIdSpan.textContent = currentSessionId.substring(0, 8) + '...';
        }
    } else {
        statusDiv.className = 'status inactive';
        statusDiv.textContent = '⏸️ Monitoring disabled';
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
        exportBtn.style.display = currentSessionId ? 'block' : 'none';
        sessionInfoDiv.style.display = 'none';
    }
}

// Event listeners
startBtn.addEventListener('click', startMonitoring);
stopBtn.addEventListener('click', stopMonitoring);
exportBtn.addEventListener('click', exportSession);

// Initialize on load
init();
