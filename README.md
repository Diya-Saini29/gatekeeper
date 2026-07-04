# Gatekeeper - Intelligent Document Q&A System

**An extraction-based RAG system for fast, cost-optimized document retrieval and question answering.**

## 🎯 What It Does

Gatekeeper is a multi-document question answering system that intelligently retrieves and extracts relevant information from uploaded documents.

### Key Features

- ✅ **Multi-Document Support** - Upload PDFs and text files
- ✅ **Semantic Search** - Find relevant documents using embeddings
- ✅ **Fast Extraction** - Get answers in milliseconds
- ✅ **Zero Cost** - Pure extraction, no LLM calls
- ✅ **Real-time Analytics** - Track queries and performance
- ✅ **Source Attribution** - Every answer cites its source document
- ✅ **Quality Verification** - Confidence scoring on answers
- ✅ **REST API** - Easy integration with other systems
- ✅ **Dashboard UI** - Web interface for interaction

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Avg Query Latency** | 50-200ms |
| **Cost per Query** | $0.00 (extraction only) |
| **Document Retrieval** | Semantic similarity (FastEmbed) |
| **Quality Score** | 0.6-0.95 on test queries |
| **Scalability** | Handles 100+ documents |

### Example Performance
Query: "name of mentor?"
Response Time: 120ms
Cost: $0.00
Quality: 0.85
Answer: "Faculty Mentor Name Dr. [extracted from document]"
---

## 🏗️ Architecture
User Query
↓
[Embedding Layer] - FastEmbed ONNX model
↓
[Semantic Search] - Find top-5 relevant chunks
↓
[Smart Extraction] - Extract answer from chunks
├→ Exact phrase matching
├→ Sentence relevance scoring
└→ Context preservation
↓
[Quality Verification] - Confidence scoring
↓
[Analytics Tracking] - Log query + metrics
↓
User gets answer + source + confidence
### Technology Stack

**Backend:**
- `FastAPI` - REST API
- `FastEmbed` - Fast embeddings (ONNX)
- `LangChain` - Document processing
- `PyPDF2` - PDF extraction
- `SQLite` - Metadata storage

**Frontend:**
- `Streamlit` - Interactive dashboard
- `Plotly` - Analytics visualization

**Infrastructure:**
- Python 3.10+
- Virtual environment
- Local or cloud deployment

---

## 💡 How It Works

### 1. Document Upload & Chunking
PDF/TXT File
↓
Load & Extract Text
↓
Split into 1000-char chunks (200 char overlap)
↓
Create semantic embeddings (384-dimensional)
↓
Store in cache with metadata
### 2. Query Processing
User Question
↓
Embed query using same model
↓
Compare against all document embeddings
↓
Retrieve top-5 most similar chunks
↓
Extract best answer using word matching + context
↓
Return answer with source + confidence
### 3. Quality Verification

**Answer is scored on:**
- Length (50-800 chars is good)
- Word overlap with query (30%+ good)
- Source relevance (similarity > 0.7)
- Coherence checking

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip or conda
- 2GB RAM minimum
- 500MB disk space

### Installation

```bash
# Clone repository
git clone <repo-url>
cd gatekeeper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Start

#### 1. Start Backend API

```bash
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

API will be available at:
- `http://127.0.0.1:8000` - API root
- `http://127.0.0.1:8000/docs` - Swagger documentation

#### 2. Start Frontend Dashboard

```bash
streamlit run frontend/dashboard.py
```

Dashboard will open at:
- `http://127.0.0.1:8501` - Main interface

#### 3. Upload Documents

1. Go to **📄 Documents** tab
2. Click "Browse files"
3. Select PDF or TXT file
4. Click "Upload to RAG"

#### 4. Ask Questions

1. Go to **❓ Query** tab
2. Type your question
3. Click "Search"
4. View answer + sources + metrics

---

## 📚 Example Queries

### Works Well ✅
"What is the vacation policy?"
→ Retrieves policy document, extracts vacation days
"Who are the team members?"
→ Finds and lists team names from document
"What is the project timeline?"
→ Extracts timeline information with dates
"List the key benefits"
→ Retrieves benefit document sections
### Limitations ⚠️
"Today's date?"
→ Cannot answer (not in documents)
"What are your thoughts on X?"
→ Cannot synthesize opinions (extraction only)
"Compare X and Y across documents"
→ Can retrieve, but limited synthesis
---

## 🎯 Use Cases

### 1. **Company Knowledge Base**
- Upload employee handbook, policies, procedures
- Employees ask FAQs instantly
- No manual documentation searches

### 2. **Research Paper Analysis**
- Upload research papers
- Extract methodology, results, conclusions
- Find specific information quickly

### 3. **Product Documentation**
- User manuals, API docs, guides
- Users get instant answers
- Reduces support tickets

### 4. **Legal Document Review**
- Contracts, policies, agreements
- Extract terms, dates, requirements
- Quick information retrieval

---

## 📖 API Documentation

### Endpoints

#### Query Processing
POST /query
Content-Type: application/json
{
"query": "your question here",
"user_id": "user_123",
"optimization_mode": "balanced"  # cost, speed, quality
}
Response:
{
"status": "success",
"answer": "Answer text here",
"sources": [{...}],
"quality_score": 0.85,
"latency_ms": 150,
"cost_usd": 0.0
}
#### Document Management
GET /documents
→ List all loaded documents
POST /documents/upload
→ Upload new document

#### Analytics
GET /analytics
→ Get cost and performance metrics
GET /analytics/recent
→ Recent queries

#### System Health
GET /health
→ API health check

Full API docs available at `/docs` when API is running.

---

## 🧠 Technical Details

### Embedding Model

**BAAI/bge-small-en-v1.5**
- 384-dimensional embeddings
- ONNX format (fast inference)
- ~5-7ms per query
- Great for semantic search

### Chunking Strategy

- Chunk size: 1000 characters
- Overlap: 200 characters (context preservation)
- Separator: Paragraph/sentence breaks
- Prevents important context loss

### Retrieval Scoring

```python
combined_score = (
    semantic_similarity * 0.5 +  # Embedding match
    word_overlap * 0.3 +         # Query word presence
    exact_match * 0.2            # Exact phrase match
)
```

### Quality Metrics

- **Latency**: Time to get answer
- **Cost**: LLM calls (always $0 here)
- **Quality**: Answer confidence (0-1)
- **Sources**: Document attribution

---

## 📊 Dashboard Features

### 📊 Analytics Page
- Total queries processed
- Cost breakdown
- Route distribution
- Performance trends

### ❓ Query Page
- Ask questions about documents
- See answer + sources
- View quality score
- Check latency/cost

### 📄 Documents Page
- Upload new documents
- View loaded documents
- Chunk count per document
- Document metadata

### 💾 Cache Page
- Semantic cache statistics
- Clear cache if needed
- Recent query history

### ⚙️ Settings Page
- System health status
- API connectivity check
- Loaded documents count

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```dotenv
# API Configuration
API_HOST=127.0.0.1
API_PORT=8000

# Storage
DATABASE_PATH=data/documents

# Cache
CACHE_THRESHOLD=0.85

# Retrieval
SMALL_MODEL_THRESHOLD=0.70
```

### Customization

**Adjust chunk size** (in `backend/document_processor.py`):
```python
chunk_size=1000  # Increase for longer context
chunk_overlap=200  # Increase for more overlap
```

**Adjust retrieval threshold** (in `backend/rag_system.py`):
```python
if similarity > 0.25:  # Lower = more results
```

**Adjust extraction aggressiveness** (in `backend/rag_answerer.py`):
```python
good_chunks = [c for c in retrieved if c["similarity"] > 0.5]  # Higher = stricter
```

---

## 🚀 Deployment

### Local Deployment

```bash
# Run both services
python run_system.py
```

Starts:
- API on `127.0.0.1:8000`
- Dashboard on `127.0.0.1:8501`

### Production Deployment

#### Option 1: Railway

```bash
# Push to GitHub
git push

# Connect GitHub to Railway
# Set start command: python -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

#### Option 2: Streamlit Cloud

```bash
# Deploy dashboard
streamlit deploy
```

#### Option 3: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📈 Performance Tuning

### For Speed

Reduce chunk_size to 500
Reduce top_k retrieval to 3
Use smaller embedding model


### For Accuracy

Increase chunk_size to 1500
Increase top_k to 10
Use larger embedding model (if available)


### For Cost (already free, but if using LLM)

Lower similarity threshold (fewer calls)
Use extraction-only (current approach)


---

## 🧪 Testing

### Test RAG System

```bash
python test_rag_system.py
```

### Test Quality Verification

```bash
python test_advanced_features.py
```

### Test Full System

```bash
python test_rag_answerer.py
```

---

## 🐛 Troubleshooting

### "No documents loaded yet"
→ Go to Documents tab
→ Upload PDF or TXT file
→ Wait for "Upload successful"

### "API not responding"
→ Make sure API is running (python -m uvicorn...)
→ Check http://127.0.0.1:8000/health
→ Check firewall settings

### "Low quality score"
→ Question not in documents (try uploading relevant doc)
→ Try rephrasing question
→ Check if document is searchable

### "Slow responses"
→ Reduce number of documents
→ Reduce chunk overlap
→ Clear cache (Cache tab)

---

## 🏆 Strengths & Limitations

### Strengths ✅

- **Fast** - Millisecond responses
- **Free** - No LLM costs
- **Reliable** - Extraction from actual documents
- **Scalable** - Handles 100+ documents
- **Simple** - Pure extraction approach
- **Explainable** - Always shows source

### Limitations ⚠️

- **Extraction-only** - Can't synthesize answers
- **No open-ended reasoning** - Fact retrieval focused
- **Query-specific** - Works for document lookups
- **No conversation** - Single-turn Q&A
- **Limited to documents** - Can't answer general knowledge

### Best Used For
✅ Document search & retrieval
✅ FAQ systems
✅ Manual lookups
✅ Quick fact finding
✅ Knowledge base queries
❌ NOT for: General chatbot, reasoning, synthesis

---

## 📚 Project Structure
gatekeeper/
├── backend/
│   ├── api.py                  # FastAPI application
│   ├── rag_system.py           # RAG retrieval engine
│   ├── rag_answerer.py         # Answer generation
│   ├── query_analyzer.py       # Query analysis
│   ├── document_processor.py   # Document loading
│   ├── embeddings.py           # Embedding functions
│   ├── quality_verifier.py     # Quality verification
│   ├── cost_tracker.py         # Analytics
│   ├── error_handler.py        # Error handling
│   ├── semantic_cache.py       # Caching
│   └── database.py             # Database setup
│
├── frontend/
│   └── dashboard.py            # Streamlit UI
│
├── test_*.py                   # Test scripts
├── requirements.txt            # Dependencies
├── .env                        # Environment variables
├── README.md                   # This file
└── run_system.py              # Quick start script

---

## 🤝 Contributing

This is a capstone project. For improvements:

1. Fork repository
2. Create feature branch
3. Test thoroughly
4. Submit pull request

---

## 📝 License

MIT License - Free to use and modify

---

## 🎓 Learning Resources

### Understanding RAG
- [LangChain RAG Documentation](https://docs.langchain.com)
- [Vector Databases for RAG](https://www.pinecone.io/learn/vector-database)
- [Semantic Search Explained](https://huggingface.co/blog/semantic-search)

### Embeddings
- [FastEmbed GitHub](https://github.com/qdrant/fastembed)
- [Embedding Models Comparison](https://huggingface.co/spaces/mteb/leaderboard)

### Production Deployment
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment)
- [Streamlit Cloud](https://streamlit.io/cloud)

---

## 📞 Support

### Common Issues

**Q: Why is my answer incomplete?**
A: Try rephrasing question or upload more relevant documents

**Q: Can I use my own embedding model?**
A: Yes, modify `backend/embeddings.py` to use different model

**Q: How do I add more documents?**
A: Upload through dashboard or use `/documents/upload` API

**Q: Is there a limit on document size?**
A: No hard limit, but large PDFs take longer to process

---

## 🎯 Next Steps

### If you want real-time conversation:
- See `RealTime-LLM-Chat` project (separate repository)
- Streaming chat with memory
- Real LLM integration

### If you want to improve this:
- Add conversation memory
- Implement hybrid RAG + LLM
- Add voice input
- Build mobile app

---

## 📊 Statistics

- **Lines of Code**: ~2000+
- **Supported Formats**: PDF, TXT, MD
- **Embedding Dimensions**: 384
- **Max Documents**: 100+
- **Avg Query Time**: 150ms
- **Cost per Query**: $0.00

---

## 🙋 Author Notes

**Built as a capstone project to demonstrate:**
- Document processing & semantic search
- Fast retrieval systems
- Cost-optimized architecture
- Production-ready Python development
- Full-stack system design

**Key learnings:**
- Extraction-based RAG works well for fact retrieval
- LLM synthesis better as separate project
- Simple architecture beats complexity
- Focus on core strength: document search

---

## 📄 Citation

If you use Gatekeeper in research or projects, cite as:
Gatekeeper - Intelligent Document Q&A System
A multi-document extraction-based retrieval system
Built with FastAPI, FastEmbed, and Streamlit

---

## 🚀 Future Roadmap

- [ ] Conversation history
- [ ] Multi-language support
- [ ] Custom embedding models
- [ ] Export answers to PDF
- [ ] Batch query processing
- [ ] API rate limiting
- [ ] User authentication
- [ ] Advanced analytics

---

**Last Updated**: 2024
**Status**: Production Ready ✅
**Version**: 1.0.0

---

**Gatekeeper: Fast, Free, Reliable Document Q&A** 🎯
