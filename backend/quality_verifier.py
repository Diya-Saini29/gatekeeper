"""
Verify answer quality before returning to user
"""

from typing import Dict, Tuple
from backend.embeddings import embed_text, cosine_similarity


class QualityVerifier:
    """Verify answer quality"""
    
    def verify(self, query: str, answer: str, 
               sources: list) -> Tuple[float, str, bool]:
        """
        Verify answer quality
        
        Returns: (quality_score, verdict, should_escalate)
        """
        
        score = 0.5  # Start with base
        issues = []
        
        # Check 1: Answer length (should not be empty)
        if len(answer) < 20:
            score -= 0.3
            issues.append("Answer too short")
        elif len(answer) > 5000:
            score -= 0.1
            issues.append("Answer very long")
        else:
            score += 0.2
        
        # Check 2: Source relevance
        if sources:
            avg_relevance = sum(s["relevance"] for s in sources) / len(sources)
            if avg_relevance > 0.8:
                score += 0.2
            elif avg_relevance < 0.5:
                score -= 0.2
                issues.append("Low source relevance")
        else:
            score -= 0.3
            issues.append("No sources found")
        
        # Check 3: Answer coherence (basic check)
        query_embedding = embed_text(query)
        answer_embedding = embed_text(answer[:500])  # Check first 500 chars
        coherence = cosine_similarity(query_embedding, answer_embedding)
        
        if coherence > 0.7:
            score += 0.2
        elif coherence < 0.4:
            score -= 0.2
            issues.append("Low answer coherence with query")
        
        # Normalize score
        score = max(0, min(score, 1.0))
        
        # Determine verdict
        if score >= 0.8:
            verdict = "EXCELLENT"
        elif score >= 0.6:
            verdict = "GOOD"
        elif score >= 0.4:
            verdict = "ACCEPTABLE"
        else:
            verdict = "POOR"
        
        # Should escalate if quality is low
        should_escalate = score < 0.5
        
        return score, verdict, should_escalate