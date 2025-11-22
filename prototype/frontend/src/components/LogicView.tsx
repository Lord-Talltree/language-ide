import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, Grid, List, ListItem, ListItemText, Chip, Divider, CircularProgress } from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import HelpIcon from '@mui/icons-material/Help';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

interface Assertion {
    subject: string;
    predicate: string;
    object: string | null;
    condition: string | null;
    modality: string | null;
}

interface Contradiction {
    type: string;
    reason: string;
    assertion_1: Assertion;
    assertion_2: Assertion;
}

interface OpenQuestion {
    type: string;
    question: string;
    assertion: Assertion;
}

interface LogicData {
    contradictions: Contradiction[];
    open_questions: OpenQuestion[];
}

interface LogicViewProps {
    docId: string;
    assertions: Assertion[];
}

export const LogicView: React.FC<LogicViewProps> = ({ docId, assertions }) => {
    const [logicData, setLogicData] = useState<LogicData | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        if (docId) {
            fetchLogic();
        }
    }, [docId]);

    const fetchLogic = async () => {
        setLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/v0/docs/${docId}/logic`);
            if (res.ok) {
                const data = await res.json();
                setLogicData(data);
            }
        } catch (err) {
            console.error("Failed to fetch logic", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2, gap: 2 }}>
            <Grid container spacing={2} sx={{ height: '100%' }}>

                {/* Left Column: Assertions List */}
                <Grid item xs={12} md={6} sx={{ height: '100%', overflow: 'auto' }}>
                    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                        <Typography variant="h6" gutterBottom>
                            Assertions ({assertions.length})
                        </Typography>
                        <List dense>
                            {assertions.map((a, idx) => (
                                <React.Fragment key={idx}>
                                    <ListItem alignItems="flex-start">
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                            <Chip label={a.subject} size="small" color="primary" variant="outlined" />
                                            <Typography variant="body2" color="text.secondary"> &mdash; {a.predicate} &rarr; </Typography>
                                            <Chip label={a.object || "None"} size="small" color="secondary" variant="outlined" />
                                            {a.condition && (
                                                <Chip label={`If: ${a.condition}`} size="small" color="warning" icon={<HelpIcon />} />
                                            )}
                                        </Box>
                                    </ListItem>
                                    <Divider component="li" />
                                </React.Fragment>
                            ))}
                        </List>
                    </Paper>
                </Grid>

                {/* Right Column: Insights */}
                <Grid item xs={12} md={6} sx={{ height: '100%', overflow: 'auto' }}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>

                        {/* Contradictions Panel */}
                        <Paper sx={{ p: 2, flex: 1, overflow: 'auto', bgcolor: '#fff4f4' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <WarningIcon color="error" />
                                <Typography variant="h6" color="error">
                                    Contradictions ({logicData?.contradictions.length || 0})
                                </Typography>
                            </Box>

                            {loading ? <CircularProgress size={20} /> : (
                                <List>
                                    {logicData?.contradictions.map((c, idx) => (
                                        <ListItem key={idx} sx={{ bgcolor: 'white', mb: 1, borderRadius: 1, border: '1px solid #ffcdd2' }}>
                                            <ListItemText
                                                primary={c.reason}
                                                secondary={
                                                    <React.Fragment>
                                                        <Typography component="span" variant="body2" display="block">
                                                            1. {c.assertion_1.subject} {c.assertion_1.predicate} {c.assertion_1.object}
                                                        </Typography>
                                                        <Typography component="span" variant="body2" display="block">
                                                            2. {c.assertion_2.subject} {c.assertion_2.predicate} {c.assertion_2.object}
                                                        </Typography>
                                                    </React.Fragment>
                                                }
                                            />
                                        </ListItem>
                                    ))}
                                    {logicData?.contradictions.length === 0 && (
                                        <Typography variant="body2" color="text.secondary">No contradictions detected.</Typography>
                                    )}
                                </List>
                            )}
                        </Paper>

                        {/* Open Questions Panel */}
                        <Paper sx={{ p: 2, flex: 1, overflow: 'auto', bgcolor: '#fffde7' }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                                <HelpIcon color="warning" />
                                <Typography variant="h6" color="warning">
                                    Open Questions ({logicData?.open_questions.length || 0})
                                </Typography>
                            </Box>

                            {loading ? <CircularProgress size={20} /> : (
                                <List>
                                    {logicData?.open_questions.map((q, idx) => (
                                        <ListItem key={idx} sx={{ bgcolor: 'white', mb: 1, borderRadius: 1, border: '1px solid #fff9c4' }}>
                                            <ListItemText
                                                primary={q.question}
                                                secondary={`Source: ${q.assertion.subject} ${q.assertion.predicate} ...`}
                                            />
                                        </ListItem>
                                    ))}
                                    {logicData?.open_questions.length === 0 && (
                                        <Typography variant="body2" color="text.secondary">No open questions detected.</Typography>
                                    )}
                                </List>
                            )}
                        </Paper>

                    </Box>
                </Grid>
            </Grid>
        </Box>
    );
};
