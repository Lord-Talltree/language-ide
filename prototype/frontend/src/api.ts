import axios from 'axios';
import { AnalysisSummary, MeaningGraph } from './types';

const API_BASE = 'http://localhost:8000/v0';

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
    }
};
