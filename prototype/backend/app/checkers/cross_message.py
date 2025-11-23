"""
Cross-Message Contradiction Checker

Detects contradictions across messages in a session by finding
antonym pairs that reference the same entity.

Example:
  Message 1: "I want a fast application"
  Message 2: "The application should be slow"
  
  Graph has: Entity("fast"), Entity("slow"), Entity("application")
  Checker finds: "fast" and "slow" are antonyms
  Both relate to "application" → CONTRADICTION
"""

from typing import List, Set, Tuple
from app.models import MeaningGraph, Diagnostic, DiagnosticKind


class CrossMessageContradictionChecker:
    """Detects contradictions across conversation messages."""
    
    def __init__(self):
        # Antonym pairs (from oxymoron checker + common contradictions)
        self.antonym_pairs = {
            frozenset(['fast', 'slow']),
            frozenset(['quick', 'slow']),
            frozenset(['hot', 'cold']),
            frozenset(['warm', 'cold']),
            frozenset(['big', 'small']),
            frozenset(['large', 'small']),
            frozenset(['tall', 'short']),
            frozenset(['high', 'low']),
            frozenset(['good', 'bad']),
            frozenset(['happy', 'sad']),
            frozenset(['easy', 'hard']),
            frozenset(['difficult', 'easy']),
            frozenset(['strong', 'weak']),
            frozenset(['light', 'heavy']),
            frozenset(['bright', 'dark']),
            frozenset(['clean', 'dirty']),
            frozenset(['new', 'old']),
            frozenset(['young', 'old']),
            frozenset(['rich', 'poor']),
            frozenset(['cheap', 'expensive']),
            frozenset(['safe', 'dangerous']),
            frozenset(['reliable', 'unreliable']),
            frozenset(['stable', 'unstable']),
        }
    
    def check(self, graph: MeaningGraph) -> List[Diagnostic]:
        """
        Check for contradictions across messages.
        
        Strategy:
        1. Extract all entity labels (including compound ones like "fast application")
        2. Tokenize labels to find adjectives within them
        3. Find antonym pairs across all tokens
        4. Flag contradictions
        """
        import re
        
        diagnostics = []
        
        # Get all entity labels
        entity_labels = {}
        for node in graph.nodes:
            if node.type in ["Entity", "Event"]:
                entity_labels[node.id] = node.label.lower()
        
        print(f"[CROSS-MESSAGE DEBUG] Found {len(entity_labels)} entities")
        print(f"[CROSS-MESSAGE DEBUG] Entity labels: {list(entity_labels.values())}")
        
        # Tokenize all labels and track which tokens come from which entities
        # token -> list of (entity_id, full_label)
        token_to_entities = {}
        
        for entity_id, label in entity_labels.items():
            # Split on whitespace and hyphens
            tokens = set(w.lower() for w in re.split(r'[\s\-]+', label) if w and len(w) > 1)
            
            for token in tokens:
                if token not in token_to_entities:
                    token_to_entities[token] = []
                token_to_entities[token].append((entity_id, label))
        
        print(f"[CROSS-MESSAGE DEBUG] Tokens found: {list(token_to_entities.keys())}")
        
        # Check for antonym pairs in the tokens
        all_tokens = set(token_to_entities.keys())
        
        for antonym_set in self.antonym_pairs:
            antonym_list = list(antonym_set)
            if len(antonym_list) != 2:
                continue
            
            word1, word2 = antonym_list
            
            # Check if both antonyms appear as tokens
            if word1 in all_tokens and word2 in all_tokens:
                print(f"[CROSS-MESSAGE DEBUG] Found antonym pair: {word1}/{word2}")
                
                # Get entities containing these tokens
                entities1 = token_to_entities[word1]
                entities2 = token_to_entities[word2]
                
                # If they come from different entities, it's a contradiction
                # (same entity would be caught by oxymoron checker)
                entity_ids1 = {eid for eid, _ in entities1}
                entity_ids2 = {eid for eid, _ in entities2}
                
                if entity_ids1 != entity_ids2:  # Different entities
                    # Create diagnostic
                    labels1 = {lbl for _, lbl in entities1}
                    labels2 = {lbl for _, lbl in entities2}
                    
                    all_labels = labels1 | labels2
                    label_list = ', '.join(f"'{l}'" for l in all_labels)
                    
                    print(f"[CROSS-MESSAGE DEBUG] Creating diagnostic for {word1}/{word2}")
                    
                    # Use first entity as anchor
                    anchor_entity = list(entity_ids1)[0] if entity_ids1 else list(entity_ids2)[0]
                    
                    diagnostics.append(Diagnostic(
                        kind=DiagnosticKind.CONTRADICTION,
                        severity="Warning",  # Fixed: was "warning"
                        message=f"Cross-message contradiction: You mentioned both '{word1}' and '{word2}' in different messages ({label_list})",
                        node_id=anchor_entity,
                        span_start=0,
                        span_end=0
                    ))
        
        print(f"[CROSS-MESSAGE DEBUG] Total diagnostics: {len(diagnostics)}")
        return diagnostics
