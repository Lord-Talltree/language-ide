from typing import List, Dict, Any
import spacy
from app.models import MeaningGraph, Edge, EdgeRole, Provenance, NodeType

class CoreferenceResolver:
    def __init__(self):
        # Simple heuristic mapping for prototype
        self.pronouns = {
            "he": ["person", "male"],
            "him": ["person", "male"],
            "his": ["person", "male"],
            "himself": ["person", "male"],
            "she": ["person", "female"],
            "her": ["person", "female"],
            "hers": ["person", "female"],
            "herself": ["person", "female"],
            "it": ["thing", "object"],
            "its": ["thing", "object"],
            "itself": ["thing", "object"],
            "they": ["person", "thing", "plural"],
            "them": ["person", "thing", "plural"],
            "their": ["person", "thing", "plural"],
            "themselves": ["person", "thing", "plural"]
        }

    def resolve(self, doc, graph: MeaningGraph) -> MeaningGraph:
        """
        Adds SAME_AS edges between pronouns and their likely antecedents.
        """
        # Get all Entity nodes
        entities = [n for n in graph.nodes if n.type == NodeType.ENTITY]
        
        # Sort by position in text to allow lookback
        # We need to parse the ID or use span info. 
        # ID format is "ent_{start}" or "tok_{i}"
        # Let's use span start.
        # entities.sort(key=lambda n: n.span.start if n.span else 0)
        
        # UPDATE: For cross-turn resolution (SessionManager), the nodes are appended in order.
        # Sorting by span.start (which resets to 0 for each new doc) breaks this order.
        # We should trust the list order provided by the caller (SessionManager appends).
        pass
        
        new_edges = []
        
        for i, node in enumerate(entities):
            text = node.label.lower()
            
            if text in self.pronouns:
                # Look backwards for a candidate
                candidate = None
                
                # Simple lookback: Find nearest preceding entity that is NOT a pronoun
                # (or is a pronoun that has been resolved? - keep it simple for now)
                for j in range(i - 1, -1, -1):
                    prev_node = entities[j]
                    prev_text = prev_node.label.lower()
                    
                    # Skip if previous node is also a pronoun
                    if prev_text in self.pronouns:
                        continue
                        
                    # Check if candidate is a valid target for the pronoun
                    # For "he/him/his", we prefer PERSON entities.
                    # We can check the entity type from properties if available.
                    # The pipeline stores `ent.label_` in properties['label'] for entities.
                    # For tokens mapped to entities, we might not have it.
                    
                    # UPDATE: Check POS tag. Pronouns should refer to Nouns/PropNouns.
                    # Avoid linking to Adjectives (e.g. "The building is tall. It..." -> "It" shouldn't link to "tall")
                    pos = prev_node.properties.get("pos")
                    if pos and pos not in ("NOUN", "PROPN"):
                        continue
                    
                    pronoun_gender = self.pronouns[text]
                    
                    # Heuristic: If pronoun is male/female, prefer PERSON
                    if "male" in pronoun_gender or "female" in pronoun_gender:
                        # Check if node has 'PERSON' label in properties
                        # Note: pipeline.py stores spacy ent label in properties['label']
                        ent_type = prev_node.properties.get("label", "")
                        if ent_type != "PERSON":
                            # If it's not explicitly a PERSON, maybe we skip it?
                            # "dreams" is not a PERSON.
                            # But "Gregor Samsa" is.
                            continue
                            
                    candidate = prev_node
                    break
                
                if candidate:
                    # Create SAME_AS edge
                    edge = Edge(
                        source=node.id,
                        target=candidate.id,
                        role="SameAs", # Custom role for now, or add to Enum
                        provenance=[Provenance(engine_id="heuristic-coref", engine_version="0.1.0")]
                    )
                    new_edges.append(edge)
                    
        graph.edges.extend(new_edges)
        return graph
