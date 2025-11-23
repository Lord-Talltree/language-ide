/**
 * L-ide Chrome Extension - Background Service Worker
 */

console.log('[L-ide] Background service worker loaded');

// Listen for installation
chrome.runtime.onInstalled.addListener(() => {
    console.log('[L-ide] Extension installed');

    // Set default state
    chrome.storage.local.set({
        monitoring: false,
        sessionId: null
    });
});

// Handle messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[L-ide] Message received:', request);

    if (request.action === 'backend_error') {
        // Show notification about backend error
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: 'L-ide Error',
            message: 'Backend connection failed. Make sure it\'s running at http://localhost:8000'
        });
    }

    sendResponse({ received: true });
    return true;
});
