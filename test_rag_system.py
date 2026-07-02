"""
Test RAG system with sample documents
"""

from backend.rag_system import RAGSystem
import os


print("=" * 80)
print("RAG SYSTEM TEST - DOCUMENT RETRIEVAL")
print("=" * 80)

# Create sample documents for testing
sample_docs = {
    "company_policy.txt": """
COMPANY POLICIES

1. Work from Home Policy
We allow employees to work from home 3 days per week.
Approval from manager required.
Core hours: 10am-3pm in your local timezone.

2. Vacation Policy
- Employees get 20 days paid vacation per year
- Must request 2 weeks in advance
- Maximum 10 consecutive days at once
- Carry-over: Up to 5 days to next year

3. Remote Work Equipment
- Laptop: Provided by company
- Monitor: Provided if working from home >2 days/week
- Internet stipend: $50/month
- Desk: Employee responsible

4. Professional Development
- $2000/year training budget per employee
- Conferences: Up to 2 per year with approval
- Online courses: Always encouraged
- Certification: Company covers full cost
""",
    "benefits.txt": """
EMPLOYEE BENEFITS

Health Insurance:
- Medical: 90% covered by company
- Dental: 50% covered by company  
- Vision: 50% covered by company
- Dependents: Available at employee cost

401(k) Retirement Plan:
- Company matches up to 6% of salary
- Immediate eligibility
- Investment options: 20+ funds

Life Insurance:
- 2x annual salary (company paid)
- Optional additional coverage available
- Beneficiary: Configurable

Wellness Program:
- Gym membership: $50/month reimbursement
- Mental health: 6 free counseling sessions/year
- Wellness checks: Annual health screening
"""
}

# Create sample docs directory
os.makedirs("test_docs", exist_ok=True)

for filename, content in sample_docs.items():
    with open(f"test_docs/{filename}", 'w') as f:
        f.write(content)

print("\n📄 Sample documents created:")
print("   - company_policy.txt")
print("   - benefits.txt")

# Initialize RAG system
rag = RAGSystem()

# Add documents
print("\n📚 Adding documents to RAG...")
results = rag.add_documents([
    "test_docs/company_policy.txt",
    "test_docs/benefits.txt"
])

print(f"✅ Added {len(results['added'])} documents")
for doc in results["added"]:
    print(f"   - {doc['filename']}: {doc['chunks']} chunks")

# Get document info
print("\n📊 Document Information:")
info = rag.get_document_info()
print(f"   Total documents: {info['total_documents']}")
print(f"   Total chunks: {info['total_chunks']}")

# Test retrieval
print("\n🔍 TEST 1: Retrieval Test")
print("-" * 80)

test_queries = [
    "How many days vacation do employees get?",
    "What is the work from home policy?",
    "Does the company provide gym benefits?",
    "How much does the company match for 401k?",
]

for query in test_queries:
    print(f"\n📝 Query: '{query}'")
    
    results = rag.retrieve(query, top_k=2)
    
    for i, result in enumerate(results, 1):
        print(f"\n   Result {i} (Similarity: {result['similarity']:.3f})")
        print(f"   Source: {result['filename']}")
        print(f"   Text: {result['chunk'][:100]}...")

print("\n" + "=" * 80)
print("✅ RAG SYSTEM TEST COMPLETE!")
print("=" * 80)

print("\n🎯 KEY FEATURES:")
print("✅ Multi-document support (2+ documents)")
print("✅ Semantic retrieval (find relevant chunks)")
print("✅ Source tracking (knows which doc each chunk came from)")
print("✅ Configurable retrieval (top-k results)")