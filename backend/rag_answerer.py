"""
Generate answers using RAG with intelligent routing and better extraction
"""

from typing import Dict, List
import time
import re
from backend.rag_system import RAGSystem
from backend.query_analyzer import QueryAnalyzer


class RAGAnswerer:
    """Generate answers using RAG with intelligent decisions"""
    
    def __init__(self):
        self.rag = RAGSystem()
        self.analyzer = QueryAnalyzer()
    
    def add_documents(self, file_paths: List[str]) -> Dict:
        """Add documents to RAG"""
        return self.rag.add_documents(file_paths)
    
    def answer_question(self, query: str, user_id: str = "user_123") -> Dict:
        """
        Answer a question using intelligent RAG with better extraction
        """
        
        start_time = time.time()
        
        # Step 1: Analyze query
        analysis = self.analyzer.analyze(query)
        
        # Step 2: Retrieve relevant documents (get more for better filtering)
        retrieved_chunks = self.rag.retrieve(query, top_k=10)
        
        # Step 3: Filter and rank chunks intelligently
        if retrieved_chunks:
            # Get only high-quality matches
            good_chunks = [c for c in retrieved_chunks if c["similarity"] > 0.6]
            
            if not good_chunks:
                # If no high matches, use top 3
                good_chunks = retrieved_chunks[:3]
            
            # Extract answer intelligently
            answer = self._extract_best_answer(query, good_chunks)
            method = "RAG with intelligent extraction"
            routing = "rag_optimized"
        else:
            # No matches
            answer = self._answer_with_fallback(query)
            method = "No matching documents"
            routing = "fallback"
        
        # Step 4: Verify quality
        from backend.quality_verifier import QualityVerifier
        verifier = QualityVerifier()
        quality_score, verdict, _ = verifier.verify(
            query, 
            answer["text"],
            answer["sources"]
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "query": query,
            "answer": answer["text"],
            "sources": answer["sources"],
            "complexity": analysis["complexity"],
            "routing": routing,
            "method": method,
            "quality_score": quality_score,
            "retrieved_chunks_count": len(retrieved_chunks) if retrieved_chunks else 0,
            "confidence": analysis["confidence"],
            "latency_ms": latency_ms
        }
    
    def _extract_best_answer(self, query: str, chunks: List[Dict]) -> Dict:
        """
        Extract the best answer from chunks with intelligent filtering
        """
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Score each chunk for relevance to the query
        chunk_scores = []
        
        for chunk in chunks:
            chunk_text = chunk["chunk"]
            chunk_lower = chunk_text.lower()
            
            # Score 1: Exact phrase match
            exact_match_score = 1.0 if query_lower in chunk_lower else 0.0
            
            # Score 2: Word overlap
            chunk_words = set(chunk_lower.split())
            word_overlap = len(query_words & chunk_words) / len(query_words) if query_words else 0
            
            # Score 3: Semantic similarity (already have this)
            semantic_score = chunk["similarity"]
            
            # Combined score (prioritize semantic + exact match)
            combined_score = (semantic_score * 0.5) + (word_overlap * 0.3) + (exact_match_score * 0.2)
            
            chunk_scores.append({
                "chunk": chunk_text,
                "filename": chunk["filename"],
                "similarity": chunk["similarity"],
                "score": combined_score,
                "word_overlap": word_overlap
            })
        
        # Sort by combined score
        chunk_scores.sort(key=lambda x: x["score"], reverse=True)
        best_scored = chunk_scores[0] if chunk_scores else None
        
        if not best_scored:
            return {
                "text": "No relevant information found.",
                "sources": []
            }
        
        # Extract from best chunk
        answer_text = self._smart_extract(
            query,
            best_scored["chunk"],
            best_scored["score"]
        )
        
        return {
            "text": answer_text,
            "sources": [
                {
                    "filename": best_scored["filename"],
                    "relevance": best_scored["similarity"],
                    "text_preview": best_scored["chunk"][:100]
                }
            ]
        }
    
    def _smart_extract(self, query: str, chunk: str, score: float) -> str:
        """
        Intelligently extract answer from chunk
        """
        
        query_lower = query.lower()
        chunk_lower = chunk.lower()
        
        # Strategy 1: Look for sentences containing query keywords
        sentences = chunk.split(".")
        
        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Count how many query words are in this sentence
            word_count = sum(1 for word in query_lower.split() if word in sentence_lower)
            
            if word_count >= 2 or (query_lower in sentence_lower):  # At least 2 query words
                relevant_sentences.append(sentence.strip())
        
        # If we found relevant sentences, use them
        if relevant_sentences:
            answer_text = ". ".join(relevant_sentences[:3])
            if not answer_text.endswith("."):
                answer_text += "."
            return answer_text
        
        # Strategy 2: Look for the query phrase directly
        if query_lower in chunk_lower:
            # Find position and extract surrounding context
            pos = chunk_lower.find(query_lower)
            
            # Get context before and after
            start = max(0, pos - 200)
            end = min(len(chunk), pos + len(query) + 300)
            
            answer_text = chunk[start:end].strip()
            
            # Clean up
            if not answer_text.startswith(chunk[pos:pos+50]):
                answer_text = "..." + answer_text
            if end < len(chunk):
                answer_text = answer_text + "..."
            
            return answer_text
        
        # Strategy 3: Return first N sentences (fallback)
        first_sentences = sentences[:2]
        answer_text = ". ".join([s.strip() for s in first_sentences if s.strip()])
        
        if not answer_text.endswith("."):
            answer_text += "."
        
        # Limit length
        if len(answer_text) > 500:
            answer_text = answer_text[:500] + "..."
        
        return answer_text if answer_text else chunk[:200] + "..."
    
    def _answer_with_fallback(self, query: str) -> Dict:
        """Fallback for no matches"""
        
        return {
            "text": f"I couldn't find information about '{query}' in the uploaded documents. "
                    f"Please try rephrasing your question or upload documents that contain this information.",
            "sources": []
        }