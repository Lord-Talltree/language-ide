import axios from 'axios';
import { AnalysisSummary, MeaningGraph } from './types';

const API_BASE = 'http://localhost:8000/v0';

export interface SessionMetadata {
    id: string;
    name: string;
    created_at: string;
    updated_at: string;
    node_count: number;
    edge_count: number;
    diagnostic_count: number;
}

export const api = {
    createDoc: async (text: string) => {
        const response = await axios.post(`${API_BASE}/docs`, { text });
        return response.data;
    },

    analyzeDoc: async (docId: string, mode: string = "Map") => {
        const response = await axios.post<AnalysisSummary>(`${API_BASE}/analyze`, {
            docId,
            options: {
                processing_mode: mode,
                stages: ["segment", "parse", "graph"],
                detail: "full"
            }
        });
        return response.data;
    },

    getGraph: async (docId: string) => {
        const response = await axios.get<MeaningGraph>(`${API_BASE}/docs/${docId}/graph`);
        return response.data;
    },

    // Session Management
    listSessions: async () => {
        const response = await axios.get<SessionMetadata[]>(`${API_BASE}/sessions`);
        return response.data;
    },

    createSession: async (text: string = '', name?: string) => {
        const response = await axios.post<SessionMetadata>(`${API_BASE}/sessions`, {
            text,
            name,
            lang: 'en'
        });
        return response.data;
    },

    getSession: async (sessionId: string) => {
        const response = await axios.get<SessionMetadata>(`${API_BASE}/sessions/${sessionId}`);
        return response.data;
    },

    deleteSession: async (sessionId: string) => {
        const response = await axios.delete(`${API_BASE}/sessions/${sessionId}`);
        return response.data;
    },

    exportSession: async (sessionId: string, format: 'json' | 'markdown' = 'markdown') => {
        const response = await axios.get(`${API_BASE}/sessions/${sessionId}/export?format=${format}`);
        return response.data;
    }
};
