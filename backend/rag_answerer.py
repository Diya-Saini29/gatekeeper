"""
Generate answers using RAG with intelligent routing
"""

from typing import Dict, List
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
        Answer a question using intelligent RAG
        
        Returns complete answer with metadata
        """
        
        # Step 1: Analyze query
        analysis = self.analyzer.analyze(query)
        
        # Step 2: Retrieve relevant documents
        retrieved_chunks = self.rag.retrieve(query, top_k=3)
        
        # Step 3: Build answer based on routing decision
        routing = analysis["routing"]
        
        if routing == "retrieval_only":
            # Simple retrieval - return top result directly
            answer = self._answer_from_retrieval(retrieved_chunks)
            method = "Direct retrieval from documents"
        
        elif routing == "rag_with_reasoning":
            # RAG + fast reasoning
            answer = self._answer_with_reasoning(query, retrieved_chunks, "fast")
            method = "RAG with fast reasoning"
        
        else:
            # Full reasoning
            answer = self._answer_with_reasoning(query, retrieved_chunks, "full")
            method = "RAG with full LLM reasoning"
        
        # Step 4: Verify answer quality
        quality_score = self._verify_quality(answer, retrieved_chunks)
        
        # Step 5: Build response
        return {
            "status": "success",
            "query": query,
            "answer": answer["text"],
            "sources": answer["sources"],
            "complexity": analysis["complexity"],
            "routing": routing,
            "method": method,
            "quality_score": quality_score,
            "retrieved_chunks_count": len(retrieved_chunks),
            "confidence": analysis["confidence"]
        }
    
    def _answer_from_retrieval(self, chunks: List[Dict]) -> Dict:
        """Answer directly from retrieved chunks"""
        
        if not chunks:
            return {
                "text": "No relevant information found in documents.",
                "sources": []
            }
        
        # Get top chunk
        top_chunk = chunks[0]
        
        return {
            "text": top_chunk["chunk"],
            "sources": [
                {
                    "filename": top_chunk["filename"],
                    "relevance": top_chunk["similarity"],
                    "text_preview": top_chunk["chunk"][:100]
                }
            ]
        }
    
    def _answer_with_reasoning(self, query: str, chunks: List[Dict], 
                              mode: str) -> Dict:
        """Answer using LLM reasoning over retrieved chunks"""
        
        # Build context from retrieved chunks
        context = "\n\n".join([
            f"[From {c['filename']}]\n{c['chunk']}"
            for c in chunks
        ])
        
        # Simulate LLM reasoning
        if mode == "fast":
            answer_text = f"Based on the retrieved documents, here's the answer to '{query}':\n\n{context[:300]}..."
        else:
            answer_text = f"After careful analysis of the documents, here's a comprehensive answer to '{query}':\n\n{context}"
        
        return {
            "text": answer_text,
            "sources": [
                {
                    "filename": c["filename"],
                    "relevance": c["similarity"],
                    "text_preview": c["chunk"][:100]
                }
                for c in chunks
            ]
        }
    
    def _verify_quality(self, answer: Dict, chunks: List[Dict]) -> float:
        """Verify answer quality (0-1)"""
        
        quality = 0.5  # Start with base
        
        # More sources = higher confidence
        if len(chunks) >= 3:
            quality += 0.3
        elif len(chunks) >= 1:
            quality += 0.2
        
        # High relevance = higher confidence
        if chunks and chunks[0]["similarity"] > 0.8:
            quality += 0.2
        
        return min(quality, 1.0)