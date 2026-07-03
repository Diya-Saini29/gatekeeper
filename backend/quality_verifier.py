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
        
        score = 0.5
        
        # Check 1: Answer length (reasonable)
        if len(answer) < 15:
            score -= 0.4  # Too short
        elif 30 <= len(answer) <= 800:  # Good length
            score += 0.3
        elif len(answer) > 2000:
            score -= 0.2  # Too long
        else:
            score += 0.15
        
        # Check 2: Direct relevance - word overlap
        query_words = [w.lower() for w in query.split() if len(w) > 2]
        answer_words = [w.lower() for w in answer.split() if len(w) > 2]
        
        if query_words:
            overlap = len(set(query_words) & set(answer_words)) / len(query_words)
            if overlap > 0.4:
                score += 0.3
            elif overlap < 0.15:
                score -= 0.25
        
        # Check 3: Source quality
        if sources:
            for s in sources:
                sim = s.get("similarity", 0) or s.get("relevance", 0)
                if sim > 0.75:
                    score += 0.25
                elif sim < 0.45:
                    score -= 0.15
        else:
            score -= 0.2
        
        # Check 4: Avoid hallucination markers
        hallucination_markers = ["i don't know", "not found", "unclear", "unable to determine"]
        if any(marker in answer.lower() for marker in hallucination_markers):
            score -= 0.15
        
        # Normalize
        score = max(0, min(score, 1.0))
        
        # Verdict
        if score >= 0.8:
            verdict = "EXCELLENT"
        elif score >= 0.65:
            verdict = "GOOD"
        elif score >= 0.45:
            verdict = "ACCEPTABLE"
        else:
            verdict = "NEEDS IMPROVEMENT"
        
        return score, verdict, score < 0.5