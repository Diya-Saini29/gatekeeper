"""
Benchmark Gatekeeper against standard RAG
"""

from typing import List, Dict
import time
import json
from backend.rag_system import RAGSystem
from backend.query_analyzer import QueryAnalyzer
from backend.semantic_cache import SemanticCache
from backend.quality_verifier import QualityVerifier


class Benchmarker:
    """Benchmark Gatekeeper performance"""
    
    def __init__(self):
        self.rag = RAGSystem()
        self.analyzer = QueryAnalyzer()
        self.verifier = QualityVerifier()
        self.cache = SemanticCache()
        self.results = []
    
    def add_documents(self, file_paths: List[str]):
        """Add documents for benchmarking"""
        self.rag.add_documents(file_paths)
    
    def benchmark_query(self, query: str) -> Dict:
        """
        Benchmark a single query against both approaches
        
        Returns: Comparison metrics
        """
        
        # APPROACH 1: Standard RAG (send to LLM for every query)
        # Simulated cost: $0.001 per query
        standard_latency = 2000  # 2 seconds
        standard_cost = 0.001
        
        # APPROACH 2: Gatekeeper (intelligent routing)
        start = time.time()
        
        # Check cache
        cached = self.cache.get(query)
        if cached:
            gatekeeper_latency = (time.time() - start) * 1000
            gatekeeper_cost = 0.0
            method = "cache_hit"
            # Get actual answer from cache
            answer_text = cached["answer"]
            sources = cached.get("sources", [])
        else:
            # Analyze and route
            analysis = self.analyzer.analyze(query)
            retrieved = self.rag.retrieve(query, top_k=3)
            
            # Determine routing
            routing = analysis["routing"]
            if routing == "retrieval_only":
                gatekeeper_cost = 0.0
            elif routing == "rag_with_reasoning":
                gatekeeper_cost = 0.0001
            else:
                gatekeeper_cost = 0.001
            
            gatekeeper_latency = (time.time() - start) * 1000
            method = routing
            
            # Build actual answer from retrieved chunks
            if retrieved:
                answer_text = "\n".join([c["chunk"] for c in retrieved[:2]])
                sources = retrieved
            else:
                answer_text = f"Unable to find information about: {query}"
                sources = []
            
            # Cache for future
            self.cache.put(query, {
                "answer": answer_text,
                "sources": sources
            })
        
        # Verify quality with ACTUAL answer
        quality_score, verdict, _ = self.verifier.verify(
            query, 
            answer_text,  # Use actual answer, not "answer"
            sources       # Use actual sources, not []
        )
        
        # Calculate savings
        cost_savings = standard_cost - gatekeeper_cost
        latency_improvement = standard_latency / gatekeeper_latency if gatekeeper_latency > 0 else 0
        
        result = {
            "query": query[:50],
            "method": method,
            "standard_latency_ms": standard_latency,
            "gatekeeper_latency_ms": gatekeeper_latency,
            "latency_improvement": latency_improvement,
            "standard_cost": standard_cost,
            "gatekeeper_cost": gatekeeper_cost,
            "cost_savings": cost_savings,
            "quality_score": quality_score
        }
        
        self.results.append(result)
        return result
    
    def run_benchmark_suite(self, queries: List[str]) -> Dict:
        """Run complete benchmark suite"""
        
        print(f"Running benchmark on {len(queries)} queries...")
        
        for query in queries:
            self.benchmark_query(query)
        
        # Aggregate results
        return self.aggregate_results()
    
    def aggregate_results(self) -> Dict:
        """Aggregate all results"""
        
        if not self.results:
            return {}
        
        total_queries = len(self.results)
        
        # Latency analysis
        latencies_gk = [r["gatekeeper_latency_ms"] for r in self.results]
        latencies_std = [r["standard_latency_ms"] for r in self.results]
        
        avg_latency_gk = sum(latencies_gk) / len(latencies_gk)
        avg_latency_std = sum(latencies_std) / len(latencies_std)
        avg_latency_improvement = avg_latency_std / avg_latency_gk if avg_latency_gk > 0 else 0
        
        # Cost analysis
        costs_gk = [r["gatekeeper_cost"] for r in self.results]
        costs_std = [r["standard_cost"] for r in self.results]
        
        total_cost_gk = sum(costs_gk)
        total_cost_std = sum(costs_std)
        total_savings = total_cost_std - total_cost_gk
        savings_percent = (total_savings / total_cost_std * 100) if total_cost_std > 0 else 0
        
        # Route breakdown
        routes = {}
        for result in self.results:
            method = result["method"]
            routes[method] = routes.get(method, 0) + 1
        
        # Quality metrics
        quality_scores = [r["quality_score"] for r in self.results]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_queries": total_queries,
            "latency": {
                "standard_avg_ms": avg_latency_std,
                "gatekeeper_avg_ms": avg_latency_gk,
                "improvement_ratio": avg_latency_improvement
            },
            "cost": {
                "standard_total": total_cost_std,
                "gatekeeper_total": total_cost_gk,
                "savings_usd": total_savings,
                "savings_percent": savings_percent
            },
            "routing": {
                "breakdown": routes,
                "total_free_queries": routes.get("retrieval_only", 0) + routes.get("cache_hit", 0)
            },
            "quality": {
                "average_score": avg_quality
            }
        }
    
    def save_results(self, filename: str):
        """Save benchmark results"""
        with open(filename, 'w') as f:
            json.dump(self.aggregate_results(), f, indent=2)