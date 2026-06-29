"""
Test script to verify embeddings work correctly
"""

import time
import numpy as np
from backend.embeddings import (
    embed_text, 
    cosine_similarity, 
    INTENT_EMBEDDINGS
)

print("=" * 60)
print("GATEKEEPER EMBEDDINGS TEST")
print("=" * 60)

# Test 1: Single embedding speed
print("\n📊 TEST 1: Embedding Speed")
print("-" * 60)

test_queries = [
    "What's my balance?",
    "What are your hours?",
    "Can you help me?",
]

for query in test_queries:
    start = time.time()
    embedding = embed_text(query)
    latency = (time.time() - start) * 1000
    
    print(f"Query: '{query}'")
    print(f"  Latency: {latency:.2f}ms")
    print(f"  Embedding size: {len(embedding)} dimensions")
    print()

# Test 2: Similarity comparison
print("\n📊 TEST 2: Similarity Scores")
print("-" * 60)

# Compare two similar queries
query1 = embed_text("What's my balance?")
query2 = embed_text("Check my account balance")
query3 = embed_text("What are your hours?")

sim_12 = cosine_similarity(query1, query2)
sim_13 = cosine_similarity(query1, query3)

print(f"Similarity: 'What's my balance?' vs 'Check my account balance'")
print(f"  Score: {sim_12:.3f} (should be high, ~0.8+)")
print()
print(f"Similarity: 'What's my balance?' vs 'What are your hours?'")
print(f"  Score: {sim_13:.3f} (should be low, ~0.3-0.5)")
print()

# Test 3: Intent matching
print("\n📊 TEST 3: Intent Classification")
print("-" * 60)

test_intent_queries = [
    "What's my account balance?",
    "When do you close?",
    "Hello there!",
]

for query in test_intent_queries:
    query_embedding = embed_text(query)
    
    print(f"\nQuery: '{query}'")
    print("  Intent scores:")
    
    scores = {}
    for intent_name, intent_embedding in INTENT_EMBEDDINGS.items():
        score = cosine_similarity(query_embedding, intent_embedding)
        scores[intent_name] = score
    
    # Sort by score
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    for intent_name, score in sorted_scores:
        print(f"    {intent_name}: {score:.3f}")
    
    best_intent = sorted_scores[0]
    print(f"  ✅ Best match: {best_intent[0]} (confidence: {best_intent[1]:.3f})")

print("\n" + "=" * 60)
print("✅ EMBEDDINGS TEST COMPLETE!")
print("=" * 60)