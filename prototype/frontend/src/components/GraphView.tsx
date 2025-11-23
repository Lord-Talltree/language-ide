import React, { useMemo, useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { MeaningGraph, Node } from '../types';
import cytoscape from 'cytoscape';

interface GraphViewProps {
    graph: MeaningGraph | null;
    onNodeClick?: (node: Node) => void;
}

type ViewLevel = 'HIGH' | 'MID' | 'LOW';
type NodeTypeFilter = 'All' | 'Goal' | 'Event' | 'Entity' | 'Claim';

const GraphView: React.FC<GraphViewProps> = ({ graph, onNodeClick }) => {
    const [layoutMode, setLayoutMode] = React.useState<'force' | 'timeline'>('force');
    const [viewLevel, setViewLevel] = React.useState<ViewLevel>('MID');
    const [nodeTypeFilter, setNodeTypeFilter] = React.useState<NodeTypeFilter>('All');
    const [searchTerm, setSearchTerm] = React.useState<string>('');
    const cyRef = useRef<cytoscape.Core | null>(null);

    const layout = useMemo(() => {
        if (layoutMode === 'force') {
            return {
                name: 'cose',
                animate: true,
                animationDuration: 500,
                nodeRepulsion: 8000,
                idealEdgeLength: 100,
                padding: 50
            };
        } else {
            return {
                name: 'preset',
                animate: true,
                animationDuration: 500,
                padding: 50,
                fit: true
            };
        }
    }, [layoutMode]);

    const elements = useMemo(() => {
        if (!graph) return [];

        // Filter nodes based on ViewLevel
        let filteredNodes = graph.nodes;

        // ViewLevel filtering
        if (viewLevel === 'HIGH') {
            // HIGH: Only Goals
            filteredNodes = filteredNodes.filter(n => n.type === 'Goal');
        } else if (viewLevel === 'MID') {
            // MID: Goals + Events
            filteredNodes = filteredNodes.filter(n =>
                n.type === 'Goal' || n.type === 'Event'
            );
        }
        // LOW: All nodes (no filter)

        // Node type filter
        if (nodeTypeFilter !== 'All') {
            filteredNodes = filteredNodes.filter(n => n.type === nodeTypeFilter);
        }

        // Search filter
        if (searchTerm.trim()) {
            const search = searchTerm.toLowerCase();
            filteredNodes = filteredNodes.filter(n =>
                n.label.toLowerCase().includes(search) ||
                n.id.toLowerCase().includes(search)
            );
        }

        const sortedNodes = [...filteredNodes].sort((a, b) => {
            const startA = a.span ? a.span.start : 0;
            const startB = b.span ? b.span.start : 0;
            return startA - startB;
        });

        const nodes = filteredNodes.map(n => {
            let position = undefined;
            if (layoutMode === 'timeline') {
                const rank = sortedNodes.findIndex(sn => sn.id === n.id);
                const x = rank * 150;
                let y = 0;

                if (n.type === 'Event') {
                    y = 0;
                } else if (n.type === 'Entity') {
                    y = (rank % 2 === 0) ? -100 : 100;
                } else if (n.type === 'Goal') {
                    y = -200; // Goals at the top
                } else {
                    y = 200;
                }
                position = { x, y };
            }

            // Check for contradictions
            let isContradiction = false;
            if (graph.diagnostics) {
                isContradiction = graph.diagnostics.some(d =>
                    d.kind === 'Contradiction' && d.message.includes(n.label)
                );
            }

            return {
                data: {
                    id: n.id,
                    label: n.label,
                    type: n.type,
                    contradiction: isContradiction ? 'true' : 'false',
                    originalNode: n // Pass full node data including span/properties
                },
                position: position
            };
        });

        const edges = graph.edges.map((e, i) => ({
            data: { source: e.source, target: e.target, label: e.role, id: `e${i}` }
        }));

        return [...nodes, ...edges];
    }, [graph, layoutMode]);

    // Bind events
    useEffect(() => {
        if (cyRef.current && onNodeClick) {
            const cy = cyRef.current;
            const handler = (evt: any) => {
                const node = evt.target;
                const originalNode = node.data('originalNode');
                if (originalNode) {
                    onNodeClick(originalNode);
                }
            };
            cy.on('tap', 'node', handler);
            return () => {
                cy.off('tap', 'node', handler);
            };
        }
    }, [cyRef.current, onNodeClick]);

    const stylesheet = useMemo(() => [
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#9b9b9b',
                'color': '#000',
                'font-size': 12,
                'width': 70,
                'height': 70,
                'border-width': 2,
                'border-color': '#555'
            }
        },
        {
            selector: 'node[contradiction="true"]',
            style: {
                'background-color': '#ef4444', // Red-500
                'border-color': '#b91c1c',     // Red-700
                'border-width': 4
            }
        },
        {
            selector: 'node[type="Event"]',
            style: {
                'background-color': '#fbbf24',
                'shape': 'roundrectangle',
                'border-color': '#f59e0b'
            }
        },
        {
            selector: 'node[type="Entity"]',
            style: {
                'background-color': '#60a5fa',
                'shape': 'ellipse',
                'border-color': '#3b82f6'
            }
        },
        {
            selector: 'node[type="Claim"]',
            style: {
                'background-color': '#c084fc',
                'shape': 'diamond',
                'border-color': '#a855f7'
            }
        },
        {
            selector: 'node[type="Goal"]',
            style: {
                'background-color': '#10b981', // Emerald-500
                'shape': 'star',
                'border-color': '#059669',     // Emerald-600
                'width': 80,
                'height': 80
            }
        },
        // Linguistic Nuance Styles
        {
            selector: 'node[modality="possible"]',
            style: {
                'border-style': 'dashed',
                'border-width': 4
            }
        },
        {
            selector: 'node[polarity="negative"]',
            style: {
                'border-color': '#ef4444', // Red-500
                'border-width': 4
            }
        },
        {
            selector: 'edge',
            style: {
                'label': 'data(label)',
                'width': 2,
                'line-color': '#64748b',
                'target-arrow-color': '#64748b',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'color': '#000',
                'font-size': 10,
                'text-background-color': '#fff',
                'text-background-opacity': 0.8
            }
        },
        {
            selector: 'edge[label="SameAs"]',
            style: {
                'width': 1,
                'line-style': 'dashed',
                'line-color': '#94a3b8',
                'target-arrow-color': '#94a3b8',
                'opacity': 0.6,
                'target-arrow-shape': 'none'
            }
        }
    ], []);

    // Calculate stats
    const totalNodes = graph?.nodes.length || 0;
    const visibleNodes = elements.filter(e => e.data?.type).length;

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            {/* Main Control Panel */}
            <div style={{
                position: 'absolute',
                top: 10,
                right: 10,
                zIndex: 10,
                background: 'rgba(255,255,255,0.95)',
                padding: '12px',
                borderRadius: '8px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                minWidth: '280px'
            }}>
                {/* Layout Controls */}
                <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '4px', fontSize: '12px' }}>
                        Layout
                    </label>
                    <select
                        value={layoutMode}
                        onChange={(e) => setLayoutMode(e.target.value as 'force' | 'timeline')}
                        style={{
                            width: '100%',
                            padding: '6px 10px',
                            borderRadius: '4px',
                            border: '1px solid #d1d5db',
                            fontSize: '13px'
                        }}
                    >
                        <option value="force">Force (Organic)</option>
                        <option value="timeline">Timeline (Linear)</option>
                    </select>
                </div>

                {/* View Level */}
                <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '4px', fontSize: '12px' }}>
                        Hierarchy Level
                    </label>
                    <div style={{ display: 'flex', gap: '4px' }}>
                        <button
                            onClick={() => setViewLevel('HIGH')}
                            style={{
                                flex: 1,
                                padding: '6px',
                                borderRadius: '4px',
                                border: viewLevel === 'HIGH' ? '2px solid #3b82f6' : '1px solid #d1d5db',
                                background: viewLevel === 'HIGH' ? '#eff6ff' : 'white',
                                cursor: 'pointer',
                                fontSize: '12px',
                                fontWeight: viewLevel === 'HIGH' ? 'bold' : 'normal'
                            }}
                        >
                            HIGH
                        </button>
                        <button
                            onClick={() => setViewLevel('MID')}
                            style={{
                                flex: 1,
                                padding: '6px',
                                borderRadius: '4px',
                                border: viewLevel === 'MID' ? '2px solid #3b82f6' : '1px solid #d1d5db',
                                background: viewLevel === 'MID' ? '#eff6ff' : 'white',
                                cursor: 'pointer',
                                fontSize: '12px',
                                fontWeight: viewLevel === 'MID' ? 'bold' : 'normal'
                            }}
                        >
                            MID
                        </button>
                        <button
                            onClick={() => setViewLevel('LOW')}
                            style={{
                                flex: 1,
                                padding: '6px',
                                borderRadius: '4px',
                                border: viewLevel === 'LOW' ? '2px solid #3b82f6' : '1px solid #d1d5db',
                                background: viewLevel === 'LOW' ? '#eff6ff' : 'white',
                                cursor: 'pointer',
                                fontSize: '12px',
                                fontWeight: viewLevel === 'LOW' ? 'bold' : 'normal'
                            }}
                        >
                            LOW
                        </button>
                    </div>
                    <div style={{ fontSize: '10px', color: '#6b7280', marginTop: '4px' }}>
                        {viewLevel === 'HIGH' && 'Goals only'}
                        {viewLevel === 'MID' && 'Goals + Events'}
                        {viewLevel === 'LOW' && 'All nodes'}
                    </div>
                </div>

                {/* Node Type Filter */}
                <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '4px', fontSize: '12px' }}>
                        Node Type
                    </label>
                    <select
                        value={nodeTypeFilter}
                        onChange={(e) => setNodeTypeFilter(e.target.value as NodeTypeFilter)}
                        style={{
                            width: '100%',
                            padding: '6px 10px',
                            borderRadius: '4px',
                            border: '1px solid #d1d5db',
                            fontSize: '13px'
                        }}
                    >
                        <option value="All">All Types</option>
                        <option value="Goal">Goals</option>
                        <option value="Event">Events</option>
                        <option value="Entity">Entities</option>
                        <option value="Claim">Claims</option>
                    </select>
                </div>

                {/* Search */}
                <div style={{ marginBottom: '12px' }}>
                    <label style={{ display: 'block', fontWeight: 'bold', marginBottom: '4px', fontSize: '12px' }}>
                        Search
                    </label>
                    <input
                        type="text"
                        placeholder="Search nodes..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        style={{
                            width: '100%',
                            padding: '6px 10px',
                            borderRadius: '4px',
                            border: '1px solid #d1d5db',
                            fontSize: '13px'
                        }}
                    />
                    {searchTerm && (
                        <button
                            onClick={() => setSearchTerm('')}
                            style={{
                                marginTop: '4px',
                                padding: '4px 8px',
                                fontSize: '11px',
                                border: 'none',
                                background: '#ef4444',
                                color: 'white',
                                borderRadius: '3px',
                                cursor: 'pointer'
                            }}
                        >
                            Clear
                        </button>
                    )}
                </div>

                {/* Stats */}
                <div style={{
                    borderTop: '1px solid #e5e7eb',
                    paddingTop: '8px',
                    fontSize: '11px',
                    color: '#6b7280'
                }}>
                    <div>Total: {totalNodes} nodes</div>
                    <div>Visible: {visibleNodes} nodes</div>
                </div>
            </div>

            <CytoscapeComponent
                elements={elements}
                style={{ width: '100%', height: '100%' }}
                layout={layout}
                stylesheet={stylesheet as any}
                cy={(cy: cytoscape.Core) => { cyRef.current = cy; }}
            />
        </div>
    );
};

export default GraphView;
