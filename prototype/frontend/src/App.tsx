import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { api } from './api';
import { MeaningGraph, Diagnostic } from './types';
import GraphView from './components/GraphView';
import { LogicView } from './components/LogicView';
import { Dashboard } from './pages/Dashboard';

function Home() {
    const [text, setText] = useState("Gregor Samsa awoke from uneasy dreams, he found himself transformed in his bed into a gigantic insect.");
    const [docId, setDocId] = useState<string | null>(null);
    const [graph, setGraph] = useState<MeaningGraph | null>(null);
    const [mode, setMode] = useState("Map");
    const [loading, setLoading] = useState(false);
    const [view, setView] = useState<'Graph' | 'Logic'>('Graph');

    const handleAnalyze = async () => {
        setLoading(true);
        try {
            // 1. Create Doc
            const doc = await api.createDoc(text);
            setDocId(doc.id);

            // 2. Analyze
            const summary = await api.analyzeDoc(doc.id, mode);

            // 3. Fetch Graph
            const graphData = await api.getGraph(doc.id);
            setGraph(graphData);
        } catch (err) {
            console.error(err);
            alert("Error analyzing document");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container">
            <div className="sidebar">
                <h2>Language IDE</h2>
                <div style={{ marginBottom: '10px' }}>
                    <label style={{ display: 'block', marginBottom: '5px' }}>Input Text</label>
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows={12}
                        style={{ width: '100%', boxSizing: 'border-box' }}
                    />
                </div>

                <div style={{ marginBottom: '10px' }}>
                    <label style={{ marginRight: '10px' }}>Mode:</label>
                    <select value={mode} onChange={(e) => setMode(e.target.value)}>
                        <option value="Map">Map (Default)</option>
                        <option value="Fiction">Fiction</option>
                        <option value="Truth">Truth (Plugins)</option>
                    </select>
                </div>

                <button onClick={handleAnalyze} disabled={loading}>
                    {loading ? 'Analyzing...' : 'Analyze Document'}
                </button>

                <div className="diagnostics-list">
                    <h3>Diagnostics</h3>
                    {graph && graph.diagnostics.length > 0 && (
                        <div style={{
                            marginBottom: '12px',
                            padding: '8px',
                            backgroundColor: '#2d2d2d',
                            borderRadius: '4px',
                            fontSize: '0.85em'
                        }}>
                            <strong>Found {graph.diagnostics.length} issue{graph.diagnostics.length !== 1 ? 's' : ''}</strong>
                            <div style={{ marginTop: '4px', color: '#999' }}>
                                {(() => {
                                    const counts: Record<string, number> = {};
                                    graph.diagnostics.forEach(d => {
                                        counts[d.kind] = (counts[d.kind] || 0) + 1;
                                    });
                                    return Object.entries(counts).map(([kind, count]) =>
                                        `${count} ${kind}${count !== 1 ? 's' : ''}`
                                    ).join(', ');
                                })()}
                            </div>
                        </div>
                    )}
                    {graph?.diagnostics.length === 0 && <div style={{ fontStyle: 'italic', color: '#666' }}>No issues found.</div>}
                    {graph?.diagnostics.map((d, i) => (
                        <div key={i} className={`diagnostic-item diagnostic-${d.severity.toLowerCase()}`}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                <span style={{
                                    padding: '2px 6px',
                                    borderRadius: '3px',
                                    fontSize: '0.75em',
                                    fontWeight: 'bold',
                                    backgroundColor: d.severity === 'Error' ? '#f48771' : d.severity === 'Warning' ? '#cca700' : '#75beff',
                                    color: '#000'
                                }}>
                                    {d.severity === 'Error' ? '🔴 ERROR' : d.severity === 'Warning' ? '⚠️ WARNING' : 'ℹ️ INFO'}
                                </span>
                                <strong style={{ color: '#fff' }}>[{d.kind}]</strong>
                            </div>
                            <div style={{ paddingLeft: '4px' }}>{d.message}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="main">
                <div className="toolbar">
                    <span><strong>Doc ID:</strong> {docId || '-'}</span>
                    <span><strong>Nodes:</strong> {graph?.nodes.length || 0}</span>
                    <span><strong>Edges:</strong> {graph?.edges.length || 0}</span>
                    <span><strong>Ambiguities:</strong> {graph?.ambiguity_sets.length || 0}</span>
                    <div style={{ marginLeft: 'auto', display: 'flex', gap: '10px' }}>
                        <button onClick={() => setView('Graph')} disabled={!graph} style={{ fontWeight: view === 'Graph' ? 'bold' : 'normal' }}>Graph</button>
                        <button onClick={() => setView('Logic')} disabled={!graph} style={{ fontWeight: view === 'Logic' ? 'bold' : 'normal' }}>Logic</button>
                    </div>
                </div>
                <div className="graph-container">
                    {graph ? (
                        view === 'Graph' ? <GraphView graph={graph} /> : <LogicView docId={docId!} assertions={graph.assertions} />
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#555' }}>
                            Graph Visualization Area
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
        </Router>
    );
}

export default App;
