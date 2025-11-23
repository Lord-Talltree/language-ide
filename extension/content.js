/**
 * L-ide Chrome Extension - Content Script
 * Monitors ChatGPT/Claude conversations and sends to backend
 */

const API_BASE = 'http://localhost:8000/v0';
let currentSessionId = null;
let isMonitoring = false;

// Initialize
chrome.storage.local.get(['monitoring', 'sessionId'], (result) => {
    isMonitoring = result.monitoring || false;
    currentSessionId = result.sessionId || null;

    if (isMonitoring) {
        console.log('[L-ide] Monitoring enabled');
        startMonitoring();
    }
});

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'start_monitoring') {
        isMonitoring = true;
        currentSessionId = request.sessionId;
        startMonitoring();
        sendResponse({ success: true });
    } else if (request.action === 'stop_monitoring') {
        isMonitoring = false;
        stopMonitoring();
        sendResponse({ success: true });
    }
    return true;
});

function startMonitoring() {
    console.log('[L-ide] Starting conversation monitoring');

    // Detect which AI platform we're on
    const hostname = window.location.hostname;

    if (hostname.includes('openai.com')) {
        monitorChatGPT();
    } else if (hostname.includes('claude.ai')) {
        monitorClaude();
    }
}

function stopMonitoring() {
    console.log('[L-ide] Stopping monitoring');
    // Remove observers if any
}

/**
 * Monitor ChatGPT conversations
 */
function monitorChatGPT() {
    console.log('[L-ide] Monitoring ChatGPT');

    // Watch for new messages
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    // Look for user messages
                    const userMessages = node.querySelectorAll('[data-message-author-role="user"]');
                    userMessages.forEach(processMessage);
                }
            });
        });
    });

    // Start observing the chat container
    const chatContainer = document.querySelector('main') || document.body;
    observer.observe(chatContainer, {
        childList: true,
        subtree: true
    });

    // Process existing messages
    document.querySelectorAll('[data-message-author-role="user"]').forEach(processMessage);
}

/**
 * Monitor Claude conversations
 */
function monitorClaude() {
    console.log('[L-ide] Monitoring Claude');

    // Similar pattern for Claude
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) {
                    // Claude's message structure (adjust selector as needed)
                    const userMessages = node.querySelectorAll('[data-is-streaming="false"]');
                    userMessages.forEach(processMessage);
                }
            });
        });
    });

    const chatContainer = document.querySelector('main') || document.body;
    observer.observe(chatContainer, {
        childList: true,
        subtree: true
    });
}

/**
 * Process a message element
 */
const processedMessages = new Set();

async function processMessage(messageElement) {
    if (!isMonitoring) return;

    // Extract text from message
    const text = messageElement.textContent?.trim();
    if (!text || processedMessages.has(text)) return;

    processedMessages.add(text);
    console.log('[L-ide] Processing message:', text.substring(0, 50) + '...');

    try {
        // Send to backend for analysis
        const graph = await analyzeMessage(text);

        // Display diagnostics if any
        if (graph.diagnostics && graph.diagnostics.length > 0) {
            displayDiagnostics(messageElement, graph.diagnostics);
        }
    } catch (error) {
        console.error('[L-ide] Error analyzing message:', error);
    }
}

/**
 * Send message to L-ide backend for analysis
 */
async function analyzeMessage(text) {
    // Create document
    const docResponse = await fetch(`${API_BASE}/docs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang: 'en' })
    });
    const docData = await docResponse.json();

    // Analyze
    await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            docId: docData.id,
            options: { processing_mode: 'Map' }
        })
    });

    // Get graph
    const graphResponse = await fetch(`${API_BASE}/docs/${docData.id}/graph`);
    return await graphResponse.json();
}

/**
 * Display diagnostics inline with the message
 */
function displayDiagnostics(messageElement, diagnostics) {
    // Remove any existing L-ide warnings
    const existingWarning = messageElement.querySelector('.lide-warning');
    if (existingWarning) {
        existingWarning.remove();
    }

    // Create warning container
    const warningDiv = document.createElement('div');
    warningDiv.className = 'lide-warning';

    // Group by severity
    const errors = diagnostics.filter(d => d.severity === 'error');
    const warnings = diagnostics.filter(d => d.severity === 'warning');

    let html = '<div class="lide-warning-header">⚠️ L-ide Detected Issues:</div>';

    if (errors.length > 0) {
        html += '<div class="lide-errors">';
        errors.forEach(e => {
            html += `<div class="lide-error">❌ ${e.kind}: ${e.message}</div>`;
        });
        html += '</div>';
    }

    if (warnings.length > 0) {
        html += '<div class="lide-warnings">';
        warnings.forEach(w => {
            html += `<div class="lide-warning-item">⚠️ ${w.kind}: ${w.message}</div>`;
        });
        html += '</div>';
    }

    warningDiv.innerHTML = html;

    // Insert after the message
    messageElement.parentElement.insertBefore(warningDiv, messageElement.nextSibling);
}

console.log('[L-ide] Content script loaded');
