import React, { useState, useEffect, useRef } from 'react';
import GraphView from '../components/GraphView';
import { api } from '../api';
import { MeaningGraph } from '../types';

interface Message {
    id: string;
    text: string;
    diagnostics?: any[];
    timestamp: string;
}

export const Dashboard: React.FC = () => {
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [graph, setGraph] = useState<MeaningGraph | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [activeView, setActiveView] = useState<'conversation' | 'graph'>('conversation');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Create session on mount
    useEffect(() => {
        const initSession = async () => {
            try {
                const session = await api.createSession('');
                setSessionId(session.id);
            } catch (e) {
                console.error('Failed to create session:', e);
            }
        };
        initSession();
    }, []);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || !sessionId || isLoading) return;

        const userMessage = input.trim();
        setInput('');
        setIsLoading(true);

        try {
            // Send message to session-aware endpoint
            const response = await api.sendSessionMessage(sessionId, userMessage);

            // Add message with diagnostics
            const newMessage: Message = {
                id: response.message_id || Date.now().toString(),
                text: userMessage,
                diagnostics: response.diagnostics || [],
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, newMessage]);

            // Update graph with accumulated state
            if (response.graph) {
                setGraph(response.graph);
            }
        } catch (e) {
            console.error('Error sending message:', e);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div className="dashboard">
            {/* Header */}
            <div className="dashboard-header">
                <h1>L-ide - Language GPS</h1>
                <div className="view-toggle">
                    <button
                        className={activeView === 'conversation' ? 'active' : ''}
                        onClick={() => setActiveView('conversation')}
                    >
                        💬 Conversation
                    </button>
                    <button
                        className={activeView === 'graph' ? 'active' : ''}
                        onClick={() => setActiveView('graph')}
                    >
                        🗺️ Map
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="dashboard-content">
                {activeView === 'conversation' ? (
                    <div className="conversation-view">
                        {/* Messages */}
                        <div className="messages-container">
                            {messages.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon">🗺️</div>
                                    <h2>Start Your Conversation</h2>
                                    <p>Type a message to begin building your knowledge map</p>
                                    <div className="example-prompts">
                                        <button onClick={() => setInput("I want to build a fast application")}>
                                            Try: "I want to build a fast application"
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    {messages.map((msg, idx) => (
                                        <div key={msg.id} className="message-wrapper">
                                            <div className="message user-message">
                                                <div className="message-content">{msg.text}</div>
                                                <div className="message-meta">
                                                    Message {idx + 1} • {new Date(msg.timestamp).toLocaleTimeString()}
                                                </div>
                                            </div>

                                            {/* Diagnostics */}
                                            {msg.diagnostics && msg.diagnostics.length > 0 && (
                                                <div className="diagnostics">
                                                    {msg.diagnostics.map((diag, i) => (
                                                        <div
                                                            key={i}
                                                            className={`diagnostic diagnostic-${diag.severity?.toLowerCase() || 'info'}`}
                                                        >
                                                            <div className="diagnostic-icon">
                                                                {diag.severity === 'Warning' ? '⚠️' :
                                                                    diag.severity === 'Error' ? '❌' : 'ℹ️'}
                                                            </div>
                                                            <div className="diagnostic-content">
                                                                <div className="diagnostic-kind">{diag.kind}</div>
                                                                <div className="diagnostic-message">{diag.message}</div>
                                                            </div>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                    <div ref={messagesEndRef} />
                                </>
                            )}
                        </div>

                        {/* Input */}
                        <div className="input-container">
                            <textarea
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Type your message..."
                                disabled={isLoading}
                                rows={3}
                            />
                            <button
                                onClick={sendMessage}
                                disabled={!input.trim() || isLoading}
                                className="send-button"
                            >
                                {isLoading ? '⏳ Analyzing...' : '↗ Send'}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="graph-view-container">
                        {graph ? (
                            <>
                                <div className="graph-stats">
                                    <span>{graph.nodes?.length || 0} nodes</span>
                                    <span>{graph.edges?.length || 0} edges</span>
                                    <span>{graph.diagnostics?.length || 0} diagnostics</span>
                                </div>
                                <GraphView graph={graph} />
                            </>
                        ) : (
                            <div className="empty-graph">
                                <p>Send messages to build your knowledge map</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};
