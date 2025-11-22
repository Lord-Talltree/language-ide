import React, { useState, useEffect, useRef } from 'react';
import GraphView from '../components/GraphView';
import { MeaningGraph, Node } from '../types';

interface ChatMessage {
    role: 'user' | 'agent' | 'system';
    content: string;
    docId?: string; // Link to backend document
}

interface SessionState {
    graph: MeaningGraph;
    history: { text: string; doc_id: string }[];
}

interface HighlightedSpan {
    docId: string;
    start: number;
    end: number;
}

export const Dashboard: React.FC = () => {
    const [graph, setGraph] = useState<MeaningGraph | null>(null);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [highlightedSpan, setHighlightedSpan] = useState<HighlightedSpan | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const fetchSession = async () => {
        try {
            const res = await fetch('http://localhost:8000/v0/session');
            const data = await res.json();
            setGraph(data.graph);

            // Sync docIds from history to local messages
            // This is a heuristic sync since we don't store full chat state in backend yet
            const history = data.history as { text: string; doc_id: string }[];

            setMessages(prevMessages => {
                const newMessages = [...prevMessages];
                let historyIndex = 0;

                for (let i = 0; i < newMessages.length; i++) {
                    if (newMessages[i].role === 'user') {
                        // If this user message matches the current history item
                        if (historyIndex < history.length && newMessages[i].content === history[historyIndex].text) {
                            newMessages[i].docId = history[historyIndex].doc_id;
                            historyIndex++;
                        }
                    }
                }
                return newMessages;
            });

        } catch (e) {
            console.error("Failed to fetch session", e);
        }
    };

    // Poll for graph updates
    useEffect(() => {
        fetchSession();
        const interval = setInterval(fetchSession, 2000);
        return () => clearInterval(interval);
    }, []);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            const res = await fetch('http://localhost:8000/v0/chat/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });
            const data = await res.json();

            if (data.warning) {
                setMessages(prev => [
                    ...prev,
                    { role: 'system', content: data.warning },
                    { role: 'agent', content: data.response }
                ]);
            } else {
                setMessages(prev => [...prev, { role: 'agent', content: data.response }]);
            }

            // Refresh graph immediately
            fetchSession();

        } catch (e) {
            console.error("Chat error", e);
            setMessages(prev => [...prev, { role: 'system', content: "Error communicating with agent." }]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleNodeClick = (node: Node) => {
        if (!node.span) return;

        // Find which doc this node belongs to
        // Node -> properties.frame_id -> ContextFrame -> source_doc
        const frameId = node.properties?.frame_id;
        if (!frameId || !graph) return;

        const frame = graph.context_frames.find(f => f.frame_id === frameId);
        if (frame && frame.source_doc) {
            setHighlightedSpan({
                docId: frame.source_doc,
                start: node.span.start,
                end: node.span.end
            });
        }
    };

    const renderMessageContent = (msg: ChatMessage) => {
        if (msg.role !== 'user' || !msg.docId || !highlightedSpan || msg.docId !== highlightedSpan.docId) {
            return msg.content;
        }

        // Apply highlighting
        const { start, end } = highlightedSpan;
        const text = msg.content;

        if (start >= text.length) return text;

        const before = text.substring(0, start);
        const highlight = text.substring(start, end);
        const after = text.substring(end);

        return (
            <span>
                {before}
                <span className="bg-yellow-400 text-black font-bold px-1 rounded">{highlight}</span>
                {after}
            </span>
        );
    };

    const handleResolve = (warningText: string) => {
        // Try to extract the vague term from quotes, e.g. "Vague term 'file'"
        const match = warningText.match(/'([^']+)'/);
        const term = match ? match[1] : 'it';

        setInput(`I meant that '${term}' refers to `);

        // Focus input (optional, but good UX)
        // We can add a ref to the input later if needed
    };

    return (
        <div className="flex h-screen bg-gray-900 text-white overflow-hidden font-sans">
            {/* Header / Toolbar (Optional, for future) */}

            {/* Main Workspace */}
            <div className="flex flex-1 h-full">

                {/* Left: Chat Panel (30%) */}
                <div className="w-[30%] flex flex-col border-r border-gray-700 bg-gray-800/50">
                    <div className="p-3 border-b border-gray-700 bg-gray-800 flex justify-between items-center">
                        <div>
                            <h2 className="text-sm font-bold text-gray-200 uppercase tracking-wider">Conversation</h2>
                            <p className="text-[10px] text-gray-400">Interceptor Active</p>
                        </div>
                        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" title="System Online"></div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                        {messages.length === 0 && (
                            <div className="text-gray-500 text-center mt-10 text-sm">
                                Start chatting to build the map...
                            </div>
                        )}
                        {messages.map((msg, i) => {
                            const isSystemWarning = msg.content.startsWith('[SYSTEM WARNING:');

                            if (isSystemWarning) {
                                const warningText = msg.content.replace('[SYSTEM WARNING:', '').replace(']', '').trim();
                                return (
                                    <div key={i} className="flex flex-col items-start w-full my-2 animate-fade-in">
                                        <div className="max-w-[95%] p-3 rounded-lg text-sm shadow-md bg-orange-900/20 border border-orange-500/50 text-orange-200 flex gap-3 items-start">
                                            <div className="text-lg mt-0.5">⚠️</div>
                                            <div className="flex-1">
                                                <div className="font-bold text-orange-400 mb-1 text-xs uppercase tracking-wider">Safety Alert</div>
                                                <div className="leading-relaxed">{warningText}</div>
                                                <button
                                                    onClick={() => handleResolve(warningText)}
                                                    className="mt-2 text-[10px] bg-orange-500/10 hover:bg-orange-500/20 px-2 py-1 rounded border border-orange-500/30 transition-colors text-orange-300 flex items-center gap-1"
                                                >
                                                    <span>🔧</span> Resolve Ambiguity
                                                </button>
                                            </div>
                                        </div>
                                        <span className="text-[10px] text-gray-600 mt-1 ml-2 font-mono">INTERCEPTOR::AMBIGUITY_CHECK</span>
                                    </div>
                                );
                            }

                            return (
                                <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`max-w-[90%] p-3 rounded-lg text-sm shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' :
                                        msg.role === 'system' ? 'bg-red-900/30 border border-red-500/50 text-red-200' :
                                            'bg-gray-700 text-gray-200'
                                        }`}>
                                        {renderMessageContent(msg)}
                                    </div>
                                    <span className="text-[10px] text-gray-500 mt-1 capitalize opacity-70">{msg.role}</span>
                                </div>
                            );
                        })}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="p-3 bg-gray-800 border-t border-gray-700">
                        <div className="flex gap-2">
                            <input
                                className="flex-1 bg-gray-900 border border-gray-600 rounded p-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                                placeholder="Type a message..."
                                disabled={isLoading}
                            />
                            <button
                                className="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                onClick={sendMessage}
                                disabled={isLoading}
                            >
                                Send
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Map Panel (70%) */}
                <div className="flex-1 flex flex-col relative bg-gray-900">
                    <div className="absolute top-4 right-4 z-10 flex flex-col items-end pointer-events-none">
                        <div className="bg-gray-800/90 p-3 rounded-lg backdrop-blur-sm border border-gray-700 shadow-lg pointer-events-auto">
                            <h2 className="font-bold text-sm text-gray-200 flex items-center gap-2">
                                <span className="text-blue-400">◆</span> Meaning Graph
                            </h2>
                            <div className="text-[10px] text-gray-400 mt-1">
                                Click nodes to trace context
                            </div>
                        </div>
                        {/* Legend */}
                        <div className="mt-2 bg-gray-800/80 p-2 rounded border border-gray-700/50 text-[10px] text-gray-400 pointer-events-auto">
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-full bg-blue-400"></span> Entity</div>
                            <div className="flex items-center gap-2 mb-1"><span className="w-2 h-2 rounded-sm bg-yellow-400"></span> Event</div>
                            <div className="flex items-center gap-2"><span className="w-2 h-2 rotate-45 bg-green-400"></span> Goal</div>
                        </div>
                    </div>

                    {graph ? (
                        <GraphView graph={graph} onNodeClick={handleNodeClick} />
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                            <div className="text-4xl mb-4 opacity-20">🗺️</div>
                            <p>Waiting for session data...</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
