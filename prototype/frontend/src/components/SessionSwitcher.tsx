import React, { useState, useEffect } from 'react';
import { api, SessionMetadata } from '../api';

interface SessionSwitcherProps {
    currentSessionId?: string;
    onSessionSelect: (sessionId: string) => void;
    onNewSession: () => void;
}

export const SessionSwitcher: React.FC<SessionSwitcherProps> = ({
    currentSessionId,
    onSessionSelect,
    onNewSession
}) => {
    const [sessions, setSessions] = useState<SessionMetadata[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        loadSessions();
    }, []);

    const loadSessions = async () => {
        setIsLoading(true);
        try {
            const data = await api.listSessions();
            setSessions(data);
        } catch (error) {
            console.error('Failed to load sessions:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
        e.stopPropagation();
        if (!confirm('Delete this session?')) return;

        try {
            await api.deleteSession(sessionId);
            setSessions(sessions.filter(s => s.id !== sessionId));
            if (currentSessionId === sessionId) {
                // If deleting current session, switch to another or create new
                if (sessions.length > 1) {
                    const nextSession = sessions.find(s => s.id !== sessionId);
                    if (nextSession) onSessionSelect(nextSession.id);
                } else {
                    onNewSession();
                }
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    };

    const currentSession = sessions.find(s => s.id === currentSessionId);

    return (
        <div style={{ position: 'relative', marginBottom: '16px' }}>
            {/* Current Session Display */}
            <div
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    padding: '12px 16px',
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}
            >
                <div>
                    <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                        {currentSession ? currentSession.name : 'No session selected'}
                    </div>
                    {currentSession && (
                        <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                            {currentSession.node_count} nodes · {currentSession.edge_count} edges
                            {currentSession.diagnostic_count > 0 && ` · ${currentSession.diagnostic_count} issues`}
                        </div>
                    )}
                </div>
                <div style={{ fontSize: '18px', color: '#94a3b8' }}>
                    {isOpen ? '▲' : '▼'}
                </div>
            </div>

            {/* Dropdown Menu */}
            {isOpen && (
                <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    marginTop: '4px',
                    background: 'white',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                    maxHeight: '400px',
                    overflowY: 'auto',
                    zIndex: 1000
                }}>
                    {/* New Session Button */}
                    <div
                        onClick={() => {
                            onNewSession();
                            setIsOpen(false);
                        }}
                        style={{
                            padding: '12px 16px',
                            borderBottom: '1px solid #e2e8f0',
                            cursor: 'pointer',
                            background: '#eff6ff',
                            fontWeight: 'bold',
                            color: '#3b82f6'
                        }}
                    >
                        + New Session
                    </div>

                    {/* Session List */}
                    {isLoading ? (
                        <div style={{ padding: '16px', textAlign: 'center', color: '#94a3b8' }}>
                            Loading sessions...
                        </div>
                    ) : sessions.length === 0 ? (
                        <div style={{ padding: '16px', textAlign: 'center', color: '#94a3b8' }}>
                            No sessions yet
                        </div>
                    ) : (
                        sessions.map(session => (
                            <div
                                key={session.id}
                                onClick={() => {
                                    onSessionSelect(session.id);
                                    setIsOpen(false);
                                }}
                                style={{
                                    padding: '12px 16px',
                                    borderBottom: '1px solid #f1f5f9',
                                    cursor: 'pointer',
                                    background: session.id === currentSessionId ? '#f1f5f9' : 'white',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}
                                onMouseEnter={(e) => {
                                    if (session.id !== currentSessionId) {
                                        e.currentTarget.style.background = '#f8fafc';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    if (session.id !== currentSessionId) {
                                        e.currentTarget.style.background = 'white';
                                    }
                                }}
                            >
                                <div style={{ flex: 1 }}>
                                    <div style={{ fontWeight: session.id === currentSessionId ? 'bold' : 'normal', fontSize: '13px' }}>
                                        {session.name}
                                    </div>
                                    <div style={{ fontSize: '11px', color: '#94a3b8', marginTop: '2px' }}>
                                        {session.node_count} nodes · {session.edge_count} edges
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => handleDelete(session.id, e)}
                                    style={{
                                        padding: '4px 8px',
                                        fontSize: '11px',
                                        border: 'none',
                                        background: '#fee2e2',
                                        color: '#dc2626',
                                        borderRadius: '4px',
                                        cursor: 'pointer'
                                    }}
                                >
                                    Delete
                                </button>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default SessionSwitcher;
