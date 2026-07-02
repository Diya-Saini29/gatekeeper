"""
Document loading, chunking, and embedding for RAG
"""

import os
import json
from typing import List, Dict, Tuple
from pathlib import Path
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Document:
    """Represents a processed document"""
    
    def __init__(self, filename: str, content: str, chunks: List[str]):
        self.filename = filename
        self.content = content
        self.chunks = chunks
        self.chunk_count = len(chunks)
        self.metadata = {
            "filename": filename,
            "chunk_count": self.chunk_count,
            "total_length": len(content)
        }


class DocumentProcessor:
    """Process documents for RAG"""
    
    def __init__(self):
        # Chunking strategy
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,      # Reasonable chunk size
            chunk_overlap=100,   # Overlap for context
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> str:
        """Load PDF and extract text"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Failed to load PDF: {str(e)}")
    
    def load_text_file(self, file_path: str) -> str:
        """Load plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to load text file: {str(e)}")
    
    def load_document(self, file_path: str) -> str:
        """Load document (PDF or TXT)"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.load_pdf(file_path)
        elif file_ext in ['.txt', '.md']:
            return self.load_text_file(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def chunk_document(self, content: str) -> List[str]:
        """Split document into chunks"""
        chunks = self.text_splitter.split_text(content)
        return chunks
    
    def process_document(self, file_path: str) -> Document:
        """
        Load and process a document
        
        Args:
            file_path: Path to document
        
        Returns:
            Document object with chunks
        """
        filename = Path(file_path).name
        
        # Load
        content = self.load_document(file_path)
        
        # Chunk
        chunks = self.chunk_document(content)
        
        # Create document object
        doc = Document(filename, content, chunks)
        
        return doc


class DocumentManager:
    """Manage multiple documents"""
    
    def __init__(self, storage_path: str = "data/documents"):
        self.storage_path = storage_path
        self.documents: Dict[str, Document] = {}
        self.processor = DocumentProcessor()
        
        # Create storage directory
        os.makedirs(storage_path, exist_ok=True)
    
    def add_document(self, file_path: str) -> Document:
        """Add a document to the system"""
        doc = self.processor.process_document(file_path)
        self.documents[doc.filename] = doc
        
        # Save metadata
        self._save_metadata()
        
        return doc
    
    def get_all_chunks(self) -> List[Tuple[str, str]]:
        """Get all chunks from all documents"""
        # Returns: (filename, chunk_text)
        chunks = []
        for filename, doc in self.documents.items():
            for chunk in doc.chunks:
                chunks.append((filename, chunk))
        return chunks
    
    def get_document_by_name(self, filename: str) -> Document:
        """Get a specific document"""
        return self.documents.get(filename)
    
    def list_documents(self) -> List[Dict]:
        """List all documents"""
        return [
            {
                "filename": doc.filename,
                "chunks": doc.chunk_count,
                "size": doc.metadata["total_length"]
            }
            for doc in self.documents.values()
        ]
    
    def _save_metadata(self):
        """Save document metadata"""
        metadata = {
            doc.filename: doc.metadata
            for doc in self.documents.values()
        }
        
        with open(f"{self.storage_path}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)