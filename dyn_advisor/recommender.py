"""
Recommendation engine for suggesting Dynamo graphs based on user intent.
"""

from typing import Dict, List, Any, Tuple
import re


class RecommendationEngine:
    """Recommends graphs based on user intent and provides explanations."""
    
    def __init__(self, catalog):
        """
        Initialize the recommendation engine.
        
        Args:
            catalog: GraphCatalog instance
        """
        self.catalog = catalog
        self.logger = None
    
    def set_logger(self, logger):
        """Set logger for this engine."""
        self.logger = logger
    
    def recommend(self, user_intent: str, max_results: int = 5) -> List[Tuple[Dict[str, Any], float, str]]:
        """
        Recommend graphs based on user intent.
        
        Args:
            user_intent: User's intent/query
            max_results: Maximum number of results to return
            
        Returns:
            List of tuples containing (graph, score, explanation)
        """
        if self.logger:
            self.logger.info(f"Processing recommendation request: '{user_intent}'")
        
        graphs = self.catalog.get_all_graphs()
        
        if not graphs:
            if self.logger:
                self.logger.warning("No graphs available in catalog")
            return []
        
        # Score each graph
        scored_graphs = []
        for graph in graphs:
            score, explanation = self._score_graph(graph, user_intent)
            if score > 0:
                scored_graphs.append((graph, score, explanation))
        
        # Sort by score descending
        scored_graphs.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        results = scored_graphs[:max_results]
        
        if self.logger:
            self.logger.info(f"Found {len(results)} recommendations")
        
        return results
    
    def _score_graph(self, graph: Dict[str, Any], user_intent: str) -> Tuple[float, str]:
        """
        Score a graph against user intent and generate explanation.
        
        Args:
            graph: Graph metadata
            user_intent: User's intent/query
            
        Returns:
            Tuple of (score, explanation)
        """
        score = 0.0
        reasons = []
        
        intent_lower = user_intent.lower()
        intent_words = set(re.findall(r'\w+', intent_lower))
        
        # Score name match (highest weight)
        name_lower = graph['name'].lower()
        name_words = set(re.findall(r'\w+', name_lower))
        name_overlap = len(intent_words & name_words)
        if name_overlap > 0:
            score += name_overlap * 10.0
            reasons.append(f"name matches '{graph['name']}'")
        
        # Exact name match bonus
        if intent_lower in name_lower or name_lower in intent_lower:
            score += 20.0
            reasons.append(f"name closely matches query")
        
        # Score description match
        description_lower = graph['description'].lower()
        if description_lower:
            desc_words = set(re.findall(r'\w+', description_lower))
            desc_overlap = len(intent_words & desc_words)
            if desc_overlap > 0:
                score += desc_overlap * 5.0
                reasons.append(f"description contains relevant keywords")
        
        # Score category match
        category_lower = graph['category'].lower()
        category_words = set(re.findall(r'\w+', category_lower))
        category_overlap = len(intent_words & category_words)
        if category_overlap > 0:
            score += category_overlap * 7.0
            reasons.append(f"category '{graph['category']}' matches")
        
        # Score node type matches
        node_matches = 0
        for node in graph['nodes']:
            node_name_lower = node['name'].lower()
            node_type_lower = node['type'].lower()
            
            for word in intent_words:
                if word in node_name_lower or word in node_type_lower:
                    node_matches += 1
                    break
        
        if node_matches > 0:
            score += node_matches * 3.0
            reasons.append(f"contains {node_matches} relevant node(s)")
        
        # Complexity bonus for certain keywords
        complexity_keywords = ['complex', 'advanced', 'detailed', 'comprehensive']
        if any(kw in intent_lower for kw in complexity_keywords):
            if graph['node_count'] > 10:
                score += 5.0
                reasons.append(f"complex graph with {graph['node_count']} nodes")
        
        # Simplicity bonus for certain keywords
        simplicity_keywords = ['simple', 'basic', 'easy', 'quick', 'minimal']
        if any(kw in intent_lower for kw in simplicity_keywords):
            if graph['node_count'] <= 5:
                score += 5.0
                reasons.append(f"simple graph with {graph['node_count']} nodes")
        
        # Generate explanation
        if reasons:
            explanation = "Recommended because " + ", ".join(reasons) + "."
        else:
            explanation = "No specific match found."
        
        return score, explanation
    
    def explain_recommendation(self, graph: Dict[str, Any], user_intent: str) -> str:
        """
        Generate a detailed explanation for why a graph was recommended.
        
        Args:
            graph: Graph metadata
            user_intent: User's intent/query
            
        Returns:
            Detailed explanation string
        """
        score, explanation = self._score_graph(graph, user_intent)
        
        details = [
            f"Graph: {graph['name']}",
            f"Score: {score:.1f}",
            f"Explanation: {explanation}",
            f"",
            f"Graph Details:",
            f"  - Description: {graph['description'] or 'N/A'}",
            f"  - Category: {graph['category']}",
            f"  - Nodes: {graph['node_count']}",
            f"  - Connectors: {graph['connector_count']}",
            f"  - Path: {graph['filepath']}",
        ]
        
        return "\n".join(details)
