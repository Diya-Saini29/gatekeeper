"""
Run comprehensive benchmarking
"""

from backend.benchmarker import Benchmarker
import json


print("=" * 80)
print("BENCHMARKING: Gatekeeper vs Standard RAG")
print("=" * 80)

benchmarker = Benchmarker()

# Add documents
print("\n📚 Loading documents...")
benchmarker.add_documents([
    "test_docs/company_policy.txt",
    "test_docs/benefits.txt"
])
print("✅ Documents loaded")

# Benchmark queries (varied complexity)
benchmark_queries = [
    # Simple lookups
    "What is the vacation policy?",
    "How many days vacation?",
    "Vacation days per year?",
    
    # Medium queries
    "What are the health insurance benefits?",
    "Does company provide gym membership?",
    "401k matching percentage?",
    
    # Complex queries
    "Compare vacation and work from home policies",
    "What are all the benefits?",
    "Explain the complete employee benefits package",
    
    # Repeated (test caching)
    "What is the vacation policy?",  # Same as first
    "How many days vacation?",  # Same as second
]

print(f"\n🧪 Running benchmark on {len(benchmark_queries)} queries...")
print("-" * 80)

results = benchmarker.run_benchmark_suite(benchmark_queries)

# Display results
print("\n" + "=" * 80)
print("📊 BENCHMARK RESULTS")
print("=" * 80)

print(f"\n📈 Summary:")
print(f"  Total queries: {results['total_queries']}")
print(f"  Latency improvement: {results['latency']['improvement_ratio']:.1f}x faster")
print(f"  Cost savings: ${results['cost']['savings_usd']:.6f} ({results['cost']['savings_percent']:.1f}%)")

print(f"\n⏱️ Latency Analysis:")
print(f"  Standard RAG avg: {results['latency']['standard_avg_ms']:.2f}ms")
print(f"  Gatekeeper avg: {results['latency']['gatekeeper_avg_ms']:.2f}ms")
print(f"  Improvement: {results['latency']['improvement_ratio']:.1f}x")

print(f"\n💰 Cost Analysis:")
print(f"  Standard RAG: ${results['cost']['standard_total']:.6f}")
print(f"  Gatekeeper: ${results['cost']['gatekeeper_total']:.6f}")
print(f"  Savings: ${results['cost']['savings_usd']:.6f} ({results['cost']['savings_percent']:.1f}%)")

print(f"\n🔀 Route Distribution:")
for route, count in results['routing']['breakdown'].items():
    percentage = (count / results['total_queries']) * 100
    print(f"  {route}: {count} queries ({percentage:.1f}%)")

print(f"  Free queries: {results['routing']['total_free_queries']}/{results['total_queries']}")

print(f"\n✅ Quality Score: {results['quality']['average_score']:.2f}/1.0")

# Save results
benchmarker.save_results("benchmark_results.json")
print(f"\n📁 Results saved to benchmark_results.json")

print("\n" + "=" * 80)
print("✅ BENCHMARKING COMPLETE!")
print("=" * 80)

print("""
🎯 KEY METRICS:

✅ Cost Optimization: {:.1f}% savings vs standard RAG
✅ Speed Improvement: {:.1f}x faster on average
✅ Quality Maintained: {:.2f}/1.0 quality score
✅ Free Route Usage: {}/{} queries ({:.1f}%)

This demonstrates Gatekeeper's effectiveness at:
1. Reducing costs through intelligent routing
2. Improving latency through semantic caching
3. Maintaining quality through verification
""".format(
    results['cost']['savings_percent'],
    results['latency']['improvement_ratio'],
    results['quality']['average_score'],
    results['routing']['total_free_queries'],
    results['total_queries'],
    (results['routing']['total_free_queries'] / results['total_queries']) * 100
))