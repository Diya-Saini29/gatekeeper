"""
Track costs and generate analytics
"""

from typing import Dict, List
from datetime import datetime


class QueryCost:
    """Cost of a single query"""
    
    def __init__(self, query: str, route: str, latency_ms: float):
        self.query = query
        self.route = route
        self.latency_ms = latency_ms
        self.cost_usd = 0.0  # All extraction routes are free
        self.timestamp = datetime.now().isoformat()


class CostTracker:
    """Track and analyze query costs"""
    
    def __init__(self):
        self.queries: List[QueryCost] = []
    
    def track(self, query: str, route: str, latency_ms: float):
        """Track a query cost"""
        cost = QueryCost(query, route, latency_ms)
        self.queries.append(cost)
    
    def get_analytics(self) -> Dict:
        """Get cost analytics"""
        
        if not self.queries:
            return {
                "total_queries": 0,
                "total_cost": 0,
                "route_breakdown": {}
            }
        
        total_cost = sum(q.cost_usd for q in self.queries)
        avg_latency = sum(q.latency_ms for q in self.queries) / len(self.queries)
        
        route_breakdown = {}
        for route in set(q.route for q in self.queries):
            queries_on_route = [q for q in self.queries if q.route == route]
            if queries_on_route:
                route_breakdown[route] = {
                    "count": len(queries_on_route),
                    "cost": sum(q.cost_usd for q in queries_on_route),
                    "percentage": len(queries_on_route) / len(self.queries) * 100
                }
        
        standard_cost = len(self.queries) * 0.001
        savings = standard_cost - total_cost
        savings_percent = (savings / standard_cost * 100) if standard_cost > 0 else 0
        
        return {
            "total_queries": len(self.queries),
            "total_cost": total_cost,
            "avg_latency_ms": avg_latency,
            "route_breakdown": route_breakdown,
            "standard_rag_cost": standard_cost,
            "optimized_cost": total_cost,
            "savings_usd": savings,
            "savings_percent": savings_percent
        }
    
    def get_recent_queries(self, n: int = 10) -> List[Dict]:
        """Get recent queries"""
        return [
            {
                "query": q.query[:50],
                "route": q.route,
                "cost": q.cost_usd,
                "latency_ms": q.latency_ms,
                "timestamp": q.timestamp
            }
            for q in self.queries[-n:]
        ]