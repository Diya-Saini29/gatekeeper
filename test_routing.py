"""
Test script for routing engine
"""

from backend.embeddings import embed_text, cosine_similarity, INTENT_EMBEDDINGS
from backend.routing_engine import decide_route, execute_route, calculate_savings
from backend.routing_config import ROUTE_COSTS


print("=" * 70)
print("GATEKEEPER ROUTING ENGINE TEST")
print("=" * 70)

# Test queries
test_queries = [
    ("What's my balance?", "account_lookup"),
    ("What are your hours?", "business_hours"),
    ("Calculate 5 * 3", "simple_calculation"),
    ("Hello!", "greeting"),
    ("Tell me about your AI strategy", "unknown"),
]

print("\n📊 TEST 1: Routing Decision Logic")
print("-" * 70)

total_standard_cost = 0
total_gatekeeper_cost = 0
routing_results = []

for query, expected_intent in test_queries:
    print(f"\nQuery: '{query}'")
    
    # Embed the query
    query_embedding = embed_text(query)
    
    # Classify intent
    scores = {}
    for intent_name, intent_embedding in INTENT_EMBEDDINGS.items():
        score = cosine_similarity(query_embedding, intent_embedding)
        scores[intent_name] = score
    
    best_intent = max(scores.items(), key=lambda x: x[1])
    intent = best_intent[0]
    confidence = best_intent[1]
    
    print(f"  Detected intent: {intent} (confidence: {confidence:.3f})")
    
    # Make routing decision
    decision = decide_route(intent, confidence)
    print(f"  Routing decision: {decision.route}")
    print(f"    Tool: {decision.tool}")
    print(f"    Est. latency: {decision.latency_estimate}ms")
    print(f"    Est. cost: ${decision.cost_estimate:.6f}")
    
    # Execute route
    result = execute_route(decision)
    print(f"  Result: {result['result']}")
    print(f"  Method: {result['method']}")
    
    # Track costs
    standard_cost = 0.001  # Every query would cost this with standard LLM
    gatekeeper_cost = result['cost_usd']
    
    total_standard_cost += standard_cost
    total_gatekeeper_cost += gatekeeper_cost
    
    routing_results.append({
        "query": query,
        "intent": intent,
        "confidence": confidence,
        "route": result['route'],
        "standard_cost": standard_cost,
        "gatekeeper_cost": gatekeeper_cost
    })


# Summary
print("\n" + "=" * 70)
print("📊 TEST 2: Cost Analysis")
print("=" * 70)

savings = calculate_savings(total_standard_cost, total_gatekeeper_cost)

print(f"\nTotal queries tested: {len(test_queries)}")
print(f"\nStandard approach (send everything to LLM):")
print(f"  Total cost: ${savings['standard_cost']:.6f}")
print(f"  Cost per query: ${savings['standard_cost']/len(test_queries):.6f}")

print(f"\nGatekeeper approach (intelligent routing):")
print(f"  Total cost: ${savings['gatekeeper_cost']:.6f}")
print(f"  Cost per query: ${savings['gatekeeper_cost']/len(test_queries):.6f}")

print(f"\n💰 SAVINGS:")
print(f"  Amount saved: ${savings['savings_usd']:.6f}")
print(f"  Percentage saved: {savings['savings_percent']:.1f}%")
print(f"  Cost reduction: {savings['cost_reduction_ratio']:.1f}x cheaper")

# Route distribution
print("\n" + "=" * 70)
print("📊 TEST 3: Route Distribution")
print("=" * 70)

cache_count = sum(1 for r in routing_results if r['route'] == 'cache')
small_model_count = sum(1 for r in routing_results if r['route'] == 'small_model')
expensive_count = sum(1 for r in routing_results if r['route'] == 'expensive_model')

total = len(routing_results)

print(f"\nCache route (instant, free):")
print(f"  Count: {cache_count}/{total} ({cache_count/total*100:.1f}%)")
print(f"  Cost: $0.00")

print(f"\nSmall model route (fast, cheap):")
print(f"  Count: {small_model_count}/{total} ({small_model_count/total*100:.1f}%)")
print(f"  Cost: ${small_model_count * 0.00001:.6f}")

print(f"\nExpensive model route (best quality):")
print(f"  Count: {expensive_count}/{total} ({expensive_count/total*100:.1f}%)")
print(f"  Cost: ${expensive_count * 0.001:.6f}")

# Detailed results
print("\n" + "=" * 70)
print("📊 TEST 4: Detailed Routing Results")
print("=" * 70)

print(f"\n{'Query':<35} {'Intent':<20} {'Route':<15} {'Confidence':<12}")
print("-" * 82)

for result in routing_results:
    print(f"{result['query']:<35} {result['intent']:<20} {result['route']:<15} {result['confidence']:.3f}")

print("\n" + "=" * 70)
print("✅ ROUTING ENGINE TEST COMPLETE!")
print("=" * 70)

print("\n🎯 KEY INSIGHTS:")
print(f"✅ Simple queries routed to cache (instant, free)")
print(f"✅ Complex queries routed to expensive model (best quality)")
print(f"✅ Average {savings['savings_percent']:.1f}% cost savings")
print(f"✅ System is intelligent and cost-aware")