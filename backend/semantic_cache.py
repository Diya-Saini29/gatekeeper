"""
Semantic caching - avoid redundant LLM calls
"""

from typing import Optional, Dict, List
import json
from datetime import datetime, timedelta
from backend.embeddings import embed_text, cosine_similarity


class SemanticCache:
    """Cache answers for semantically similar queries"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.cache = {}  # {query_embedding_hash: cached_result}
        self.threshold = similarity_threshold
    
    def get(self, query: str) -> Optional[Dict]:
        """
        Try to get cached answer for similar query
        
        Returns: Cached answer if found, None otherwise
        """
        query_embedding = embed_text(query)
        
        # Check all cached queries
        for cache_key, cached_data in self.cache.items():
            cached_embedding = cached_data["embedding"]
            similarity = cosine_similarity(query_embedding, cached_embedding)
            
            # Check if similar enough
            if similarity >= self.threshold:
                return cached_data["result"]
        
        return None
    
    def put(self, query: str, result: Dict):
        """Cache an answer"""
        query_embedding = embed_text(query)
        cache_key = hash(str(query_embedding))
        
        self.cache[cache_key] = {
            "query": query,
            "embedding": query_embedding,
            "result": result,
            "cached_at": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_queries": len(self.cache),
            "threshold": self.threshold
        }
    
    def clear(self):
        """Clear cache"""
        self.cache.clear()