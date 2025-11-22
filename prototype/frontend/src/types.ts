export interface Span {
    start: number;
    end: number;
    text: string;
}

export interface Provenance {
    engine_id: string;
    engine_version: string;
    confidence: number;
    receipts: any[];
}

export interface Node {
    id: string;
    type: "Entity" | "Event" | "Claim" | "ContextFrame";
    label: string;
    span?: Span;
    properties: Record<string, any>;
}

export interface Edge {
    source: string;
    target: string;
    role: string;
    provenance?: Provenance[];
}

export interface AmbiguityAlternative {
    label: string;
    weight: number;
    delta: any;
}

export interface AmbiguitySet {
    id: string;
    dimension: string;
    alternatives: AmbiguityAlternative[];
}

export interface Diagnostic {
    kind: string;
    severity: "Info" | "Warning" | "Error";
    message: string;
    provenance?: Provenance[];
}

export interface Assertion {
    subject: string;
    predicate: string;
    object: string | null;
    condition: string | null;
    modality: string | null;
}

export interface MeaningGraph {
    nodes: Node[];
    edges: Edge[];
    assertions: Assertion[];
    ambiguity_sets: AmbiguitySet[];
    context_frames: any[];
    diagnostics: Diagnostic[];
    provenance: Provenance[];
}

export interface AnalysisSummary {
    docId: string;
    graph_summary: { nodes: number; edges: number };
    top_diagnostics: Diagnostic[];
}
