"""
Analyze queries to determine complexity and routing strategy
"""

from typing import Dict, Tuple
from backend.embeddings import embed_text, cosine_similarity, INTENT_EMBEDDINGS


class QueryAnalyzer:
    """Analyze query to determine complexity and routing"""
    
    def analyze(self, query: str) -> Dict:
        """
        Analyze query and return:
        - Complexity score (0-1)
        - Query type
        - Confidence in classification
        - Suggested routing
        """
        
        # 1. Analyze query characteristics
        complexity = self._estimate_complexity(query)
        
        # 2. Classify query type
        query_embedding = embed_text(query)
        query_type, confidence = self._classify_query(query_embedding)
        
        # 3. Determine routing
        routing = self._determine_routing(complexity, confidence, query_type)
        
        return {
            "query": query,
            "complexity": complexity,
            "query_type": query_type,
            "confidence": confidence,
            "routing": routing
        }
    
    def _estimate_complexity(self, query: str) -> float:
        """Estimate query complexity (0-1)"""
        
        score = 0.0
        
        # Factor 1: Query length
        if len(query) > 150:
            score += 0.2  # Long queries often complex
        elif len(query) > 50:
            score += 0.1
        
        # Factor 2: Question words (simple vs complex)
        simple_questions = ["what", "how many", "where", "when"]
        complex_questions = ["why", "compare", "explain", "analyze", "how"]
        
        query_lower = query.lower()
        
        if any(q in query_lower for q in simple_questions):
            score += 0.1
        
        if any(q in query_lower for q in complex_questions):
            score += 0.3
        
        # Factor 3: Multiple questions?
        if query.count("?") > 1:
            score += 0.2
        
        # Normalize to 0-1
        return min(score, 1.0)
    
    def _classify_query(self, query_embedding) -> Tuple[str, float]:
        """Classify query type"""
        
        # Use existing intent embeddings if available
        try:
            scores = {}
            for intent_name, intent_embedding in INTENT_EMBEDDINGS.items():
                score = cosine_similarity(query_embedding, intent_embedding)
                scores[intent_name] = score
            
            best_intent = max(scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        
        except:
            # Fallback if no intent embeddings
            return "general_query", 0.5
    
    def _determine_routing(self, complexity: float, 
                          confidence: float, query_type: str) -> str:
        """Determine which route to use"""
        
        # High confidence + low complexity = Pure retrieval
        if confidence > 0.85 and complexity < 0.3:
            return "retrieval_only"
        
        # Medium confidence + medium complexity = RAG + fast reasoning
        elif confidence > 0.65 and complexity < 0.6:
            return "rag_with_reasoning"
        
        # Low confidence or high complexity = Full LLM reasoning
        else:
            return "rag_with_full_reasoning"