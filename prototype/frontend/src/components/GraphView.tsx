import React, { useMemo, useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import { MeaningGraph, Node } from '../types';
import cytoscape from 'cytoscape';

interface GraphViewProps {
    graph: MeaningGraph | null;
    onNodeClick?: (node: Node) => void;
}

const GraphView: React.FC<GraphViewProps> = ({ graph, onNodeClick }) => {
    const [layoutMode, setLayoutMode] = React.useState<'force' | 'timeline'>('force');
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

        const sortedNodes = [...graph.nodes].sort((a, b) => {
            const startA = a.span ? a.span.start : 0;
            const startB = b.span ? b.span.start : 0;
            return startA - startB;
        });

        const nodes = graph.nodes.map(n => {
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

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <div style={{ position: 'absolute', top: 10, right: 10, zIndex: 10, background: 'rgba(255,255,255,0.8)', padding: 5, borderRadius: 4 }}>
                <label style={{ marginRight: 10, fontWeight: 'bold' }}>Layout:</label>
                <select
                    value={layoutMode}
                    onChange={(e) => setLayoutMode(e.target.value as 'force' | 'timeline')}
                    style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #ccc' }}
                >
                    <option value="force">Force (Organic)</option>
                    <option value="timeline">Timeline (Linear)</option>
                </select>
            </div>
            <CytoscapeComponent
                elements={elements}
                style={{ width: '100%', height: '100%' }}
                layout={layout}
                stylesheet={stylesheet as any}
                cy={(cy) => { cyRef.current = cy; }}
            />
        </div>
    );
};

export default GraphView;
