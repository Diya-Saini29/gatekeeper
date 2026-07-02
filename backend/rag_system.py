"""
Real RAG system - retrieval + generation
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from backend.embeddings import embed_text, cosine_similarity
from backend.document_processor import DocumentManager


class RAGSystem:
    """Retrieval Augmented Generation System"""
    
    def __init__(self, storage_path: str = "data/documents"):
        self.doc_manager = DocumentManager(storage_path)
        self.chunks_cache = []
        self.embeddings_cache = {}
    
    def add_documents(self, file_paths: List[str]) -> Dict:
        """Add multiple documents to RAG"""
        results = {
            "added": [],
            "errors": []
        }
        
        for file_path in file_paths:
            try:
                doc = self.doc_manager.add_document(file_path)
                results["added"].append({
                    "filename": doc.filename,
                    "chunks": doc.chunk_count
                })
            except Exception as e:
                results["errors"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        # Rebuild cache after adding documents
        self._rebuild_cache()
        
        return results
    
    def _rebuild_cache(self):
        """Rebuild embeddings cache for all chunks"""
        self.chunks_cache = self.doc_manager.get_all_chunks()
        self.embeddings_cache = {}
        
        for i, (filename, chunk) in enumerate(self.chunks_cache):
            embedding = embed_text(chunk)
            self.embeddings_cache[i] = {
                "filename": filename,
                "chunk": chunk,
                "embedding": embedding
            }
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks
        
        Args:
            query: User query
            top_k: Number of results to return
        
        Returns:
            List of relevant chunks with sources
        """
        # Embed query
        query_embedding = embed_text(query)
        
        # Score all chunks
        scores = []
        for chunk_id, data in self.embeddings_cache.items():
            similarity = cosine_similarity(
                query_embedding,
                data["embedding"]
            )
            scores.append({
                "chunk_id": chunk_id,
                "filename": data["filename"],
                "chunk": data["chunk"],
                "similarity": similarity
            })
        
        # Sort by similarity and return top-k
        scores.sort(key=lambda x: x["similarity"], reverse=True)
        results = scores[:top_k]
        
        return results
    
    def get_document_info(self) -> Dict:
        """Get information about loaded documents"""
        return {
            "total_documents": len(self.doc_manager.documents),
            "total_chunks": len(self.chunks_cache),
            "documents": self.doc_manager.list_documents()
        }