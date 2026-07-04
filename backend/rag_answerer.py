"""
Generate answers using RAG with intelligent extraction (extraction-only)
"""

from typing import Dict, List
import time
from backend.rag_system import RAGSystem
from backend.query_analyzer import QueryAnalyzer


class RAGAnswerer:
    """Generate answers using RAG extraction"""
    
    def __init__(self):
        self.rag = RAGSystem()
        self.analyzer = QueryAnalyzer()
    
    def add_documents(self, file_paths: List[str]) -> Dict:
        """Add documents to RAG"""
        return self.rag.add_documents(file_paths)
    
    def answer_question(self, query: str, user_id: str = "user_123") -> Dict:
        """
        Answer a question using intelligent extraction from documents
        """
        
        start_time = time.time()
        
        # Step 1: Analyze query
        analysis = self.analyzer.analyze(query)
        
        # Step 2: Retrieve relevant documents
        retrieved_chunks = self.rag.retrieve(query, top_k=5)
        
        # Step 3: Extract answer
        if retrieved_chunks and retrieved_chunks[0]["similarity"] > 0.4:
            good_chunks = [c for c in retrieved_chunks if c["similarity"] > 0.5]
            if not good_chunks:
                good_chunks = retrieved_chunks[:2]
            
            answer = self._extract_best_answer(query, good_chunks)
            routing = "extraction"
            method = "RAG with Extraction"
        else:
            answer = self._answer_with_fallback(query)
            routing = "fallback"
            method = "No matching documents"
        
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
            "latency_ms": latency_ms,
            "cost_usd": 0.0
        }
    
    def _extract_best_answer(self, query: str, chunks: List[Dict]) -> Dict:
        """
        Extract best answer from chunks
        """
        
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        chunk_scores = []
        
        for chunk in chunks:
            chunk_text = chunk["chunk"]
            chunk_lower = chunk_text.lower()
            
            exact_match = 1.0 if query_lower in chunk_lower else 0.0
            chunk_words = set(chunk_lower.split())
            word_overlap = len(query_words & chunk_words) / len(query_words) if query_words else 0
            semantic = chunk["similarity"]
            
            combined = (semantic * 0.5) + (word_overlap * 0.3) + (exact_match * 0.2)
            
            chunk_scores.append({
                "chunk": chunk_text,
                "filename": chunk["filename"],
                "similarity": chunk["similarity"],
                "score": combined
            })
        
        chunk_scores.sort(key=lambda x: x["score"], reverse=True)
        best = chunk_scores[0] if chunk_scores else None
        
        if not best:
            return {
                "text": "No relevant information found.",
                "sources": []
            }
        
        answer_text = self._smart_extract(query, best["chunk"])
        
        return {
            "text": answer_text,
            "sources": [
                {
                    "filename": best["filename"],
                    "relevance": best["similarity"],
                    "text_preview": best["chunk"][:100]
                }
            ]
        }
    
    def _smart_extract(self, query: str, chunk: str) -> str:
        """
        Intelligently extract answer from chunk
        """
        
        query_lower = query.lower()
        chunk_lower = chunk.lower()
        
        sentences = chunk.split(".")
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            word_count = sum(1 for word in query_lower.split() if word in sentence_lower)
            
            if word_count >= 2 or (query_lower in sentence_lower):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            answer_text = ". ".join(relevant_sentences[:3])
            if not answer_text.endswith("."):
                answer_text += "."
            return answer_text
        
        if query_lower in chunk_lower:
            pos = chunk_lower.find(query_lower)
            start = max(0, pos - 200)
            end = min(len(chunk), pos + len(query) + 300)
            
            answer_text = chunk[start:end].strip()
            if start > 0:
                answer_text = "..." + answer_text
            if end < len(chunk):
                answer_text = answer_text + "..."
            
            return answer_text
        
        first_sentences = sentences[:2]
        answer_text = ". ".join([s.strip() for s in first_sentences if s.strip()])
        
        if not answer_text.endswith("."):
            answer_text += "."
        
        if len(answer_text) > 500:
            answer_text = answer_text[:500] + "..."
        
        return answer_text if answer_text else chunk[:200] + "..."
    
    def _answer_with_fallback(self, query: str) -> Dict:
        """Fallback for no matches"""
        
        return {
            "text": f"I couldn't find information about '{query}' in the uploaded documents. "
                    f"Please upload relevant documents or rephrase your question.",
            "sources": []
        }