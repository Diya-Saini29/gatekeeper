"""
FastAPI backend - REST API for Gatekeeper
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import time
import os
from datetime import datetime

from backend.rag_answerer import RAGAnswerer
from backend.semantic_cache import SemanticCache
from backend.quality_verifier import QualityVerifier
from backend.cost_tracker import CostTracker
from backend.error_handler import InputValidator, ErrorHandler

# Initialize FastAPI
app = FastAPI(
    title="Gatekeeper - AI Inference Optimization Platform",
    description="Intelligent RAG with cost optimization",
    version="1.0.0"
)

# Initialize components
answerer = RAGAnswerer()
cache = SemanticCache(similarity_threshold=0.85)
verifier = QualityVerifier()
tracker = CostTracker()
validator = InputValidator()
error_handler = ErrorHandler()

# Store uploaded file paths for document management
uploaded_files = []

# ==================== DATA MODELS ====================

class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    user_id: str = "user_123"
    optimization_mode: str = "balanced"  # cost, speed, quality

class QueryResponse(BaseModel):
    """Query response model"""
    status: str
    query: str
    answer: str
    sources: List[dict]
    complexity: float
    routing: str
    quality_score: float
    cost_usd: float
    latency_ms: float
    cached: bool
    cached_from_query: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    status: str
    filename: str
    chunks: int
    message: str

class AnalyticsResponse(BaseModel):
    """Analytics response"""
    total_queries: int
    total_cost: float
    avg_latency_ms: float
    savings_percent: float
    route_breakdown: dict

# ==================== ROUTES ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "documents_loaded": len(answerer.rag.doc_manager.documents),
        "cache_size": len(cache.cache)
    }

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for RAG
    
    Supported formats: PDF, TXT
    """
    try:
        # Validate file type
        if file.filename.lower().endswith(('.pdf', '.txt')):
            # Save file temporarily
            import os
            import tempfile
            
            temp_dir = "temp_uploads"
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_path = os.path.join(temp_dir, file.filename)
            
            # Write file
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            # Add to RAG
            result = answerer.add_documents([temp_path])
            
            if result["errors"]:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "filename": file.filename,
                        "chunks": 0,
                        "message": f"Error: {result['errors'][0]['error']}"
                    }
                )
            
            # Track uploaded file
            uploaded_files.append(temp_path)
            
            doc_info = result["added"][0]
            
            return {
                "status": "success",
                "filename": doc_info["filename"],
                "chunks": doc_info["chunks"],
                "message": f"Document uploaded successfully with {doc_info['chunks']} chunks"
            }
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Only PDF and TXT files are supported"
                }
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Upload failed: {str(e)}"
            }
        )

@app.get("/documents")
async def list_documents():
    """List all loaded documents"""
    docs = answerer.rag.get_document_info()
    return {
        "status": "success",
        "documents": docs
    }

@app.post("/query")
async def process_query(request: QueryRequest):
    """
    Process a user query with intelligent RAG
    
    Features:
    - Semantic caching
    - Quality verification
    - Cost tracking
    - Multiple routing strategies
    """
    
    start_time = time.time()
    
    # Step 1: Validate input
    is_valid, error_msg = validator.validate_query(request.query)
    if not is_valid:
        error_response = error_handler.handle_validation_error(
            "query", request.query, error_msg
        )
        raise HTTPException(status_code=400, detail=error_response)
    
    try:
        # Step 2: Check cache
        cached_result = cache.get(request.query)
        if cached_result:
            latency_ms = (time.time() - start_time) * 1000
            tracker.track(request.query, "cache_hit", latency_ms)
            
            return QueryResponse(
                status="success",
                query=request.query,
                answer=cached_result["answer"],
                sources=cached_result["sources"],
                complexity=cached_result["complexity"],
                routing="cache_hit",
                quality_score=cached_result["quality_score"],
                cost_usd=0.0,  # Cache is free
                latency_ms=latency_ms,
                cached=True,
                cached_from_query=request.query
            )
        
        # Step 3: Process query
        response = answerer.answer_question(request.query, request.user_id)
        
        # Step 4: Verify quality
        quality_score, verdict, should_escalate = verifier.verify(
            request.query,
            response["answer"],
            response["sources"]
        )
        
        # Step 5: Determine cost based on optimization mode
        base_cost = response["cost"] if "cost" in response else 0.001
        
        if request.optimization_mode == "cost":
            # Prioritize cheap routes
            if response["routing"] == "retrieval_only":
                cost_usd = 0.0
            else:
                cost_usd = min(base_cost, 0.0001)
        elif request.optimization_mode == "quality":
            # Use best answer regardless of cost
            cost_usd = base_cost
        else:  # balanced (default)
            cost_usd = base_cost
        
        # Step 6: Cache result
        cache.put(request.query, response)
        
        # Step 7: Track cost
        # Step 7: Track cost
        latency_ms = (time.time() - start_time) * 1000
        llm_cost = response.get("cost_usd", 0.0)
        tracker.track(request.query, response["routing"], latency_ms)
        
        # Step 8: Return response
        return QueryResponse(
            status="success",
            query=request.query,
            answer=response["answer"],
            sources=response["sources"],
            complexity=response["complexity"],
            routing=response["routing"],
            quality_score=quality_score,
            cost_usd=cost_usd,
            latency_ms=latency_ms,
            cached=False
        )
    
    except Exception as e:
        error_response = error_handler.handle_unknown_error(e)
        raise HTTPException(status_code=500, detail=error_response)

@app.get("/analytics")
async def get_analytics():
    """Get cost analytics and performance metrics"""
    analytics = tracker.get_analytics()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "analytics": analytics
    }

@app.get("/analytics/recent")
async def get_recent_queries(limit: int = 10):
    """Get recent queries"""
    queries = tracker.get_recent_queries(limit)
    
    return {
        "status": "success",
        "queries": queries
    }

@app.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    stats = cache.get_stats()
    
    return {
        "status": "success",
        "cache": stats
    }

@app.post("/cache/clear")
async def clear_cache():
    """Clear semantic cache"""
    cache.clear()
    
    return {
        "status": "success",
        "message": "Cache cleared successfully"
    }

if __name__ == "__main__":
    import uvicorn
    
    # Load from .env or use defaults
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    host = os.getenv("API_HOST", "127.0.0.1")  # Default to localhost
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)