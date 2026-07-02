"""
Test intelligent RAG answering
"""

from backend.rag_answerer import RAGAnswerer


print("=" * 80)
print("INTELLIGENT RAG ANSWERER TEST")
print("=" * 80)

answerer = RAGAnswerer()

# Add documents
print("\n📚 Loading documents...")
result = answerer.add_documents([
    "test_docs/company_policy.txt",
    "test_docs/benefits.txt"
])
print(f"✅ Documents loaded: {len(result['added'])} files")

# Test with different complexity queries
test_queries = [
    ("What is the vacation policy?", "Simple lookup"),
    ("How much does the company contribute to 401k?", "Direct fact"),
    ("Compare the work from home policy with vacation policy", "Comparison"),
    ("What are all the benefits offered by the company?", "Comprehensive"),
]

print("\n🧪 TEST: Answering Questions with Intelligent Routing")
print("-" * 80)

for query, description in test_queries:
    print(f"\n📝 Query: '{query}'")
    print(f"   Type: {description}")
    
    response = answerer.answer_question(query)
    
    print(f"   Complexity: {response['complexity']:.2f}")
    print(f"   Routing: {response['routing']}")
    print(f"   Method: {response['method']}")
    print(f"   Quality score: {response['quality_score']:.2f}")
    print(f"   Confidence: {response['confidence']:.2f}")
    print(f"\n   Answer preview: {response['answer'][:150]}...")
    print(f"\n   Sources: {len(response['sources'])} document(s)")
    for source in response["sources"]:
        print(f"      - {source['filename']} (relevance: {source['relevance']:.3f})")

print("\n" + "=" * 80)
print("✅ INTELLIGENT RAG ANSWERER TEST COMPLETE!")
print("=" * 80)

print("\n🎯 KEY FEATURES:")
print("✅ Query complexity estimation")
print("✅ Intelligent routing (retrieval-only vs reasoning)")
print("✅ Answer quality verification")
print("✅ Source tracking with relevance scores")
print("✅ Different methods for different query types")