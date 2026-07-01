"""
Routing Engine - Decides which system to use
"""

from backend.routing_config import (
    THRESHOLDS, INTENT_COMPLEXITY, ROUTE_COSTS, 
    ROUTE_LATENCIES, INTENT_TO_TOOL, MOCK_TOOLS
)


class RoutingDecision:
    """Container for routing decision"""
    
    def __init__(self, route, intent, confidence, 
                 tool=None, latency_estimate=0, cost_estimate=0.0):
        self.route = route
        self.intent = intent
        self.confidence = confidence
        self.tool = tool
        self.latency_estimate = latency_estimate
        self.cost_estimate = cost_estimate
    
    def __str__(self):
        return f"""
RoutingDecision:
  Route: {self.route}
  Intent: {self.intent}
  Confidence: {self.confidence:.3f}
  Tool: {self.tool}
  Est. Latency: {self.latency_estimate}ms
  Est. Cost: ${self.cost_estimate:.6f}
"""


def decide_route(intent: str, confidence: float) -> RoutingDecision:
    """
    Decide which route to use based on intent and confidence
    
    Args:
        intent: Classified intent (e.g., "account_lookup")
        confidence: Confidence score (0-1)
    
    Returns:
        RoutingDecision object with routing information
    """
    
    # Get complexity of this intent
    complexity = INTENT_COMPLEXITY.get(intent, 1.0)
    
    # Get corresponding tool
    tool = INTENT_TO_TOOL.get(intent, None)
    
    # Decision logic
    if confidence >= THRESHOLDS["cache"] and complexity < 0.3:
        # HIGH CONFIDENCE + LOW COMPLEXITY → USE CACHE
        route = "cache"
        latency = ROUTE_LATENCIES["cache"]
        cost = ROUTE_COSTS["cache"]
        
    elif confidence >= THRESHOLDS["small_model"] and complexity < 0.6:
        # MEDIUM CONFIDENCE + MEDIUM COMPLEXITY → USE SMALL MODEL
        route = "small_model"
        latency = ROUTE_LATENCIES["small_model"]
        cost = ROUTE_COSTS["small_model"]
        
    else:
        # LOW CONFIDENCE OR HIGH COMPLEXITY → USE EXPENSIVE MODEL
        route = "expensive_model"
        latency = ROUTE_LATENCIES["expensive_model"]
        cost = ROUTE_COSTS["expensive_model"]
    
    return RoutingDecision(
        route=route,
        intent=intent,
        confidence=confidence,
        tool=tool,
        latency_estimate=latency,
        cost_estimate=cost
    )


def execute_route(decision: RoutingDecision, user_id: str = "user_123") -> dict:
    """
    Execute the decision and return result
    
    Args:
        decision: RoutingDecision from decide_route()
        user_id: User ID for personalization
    
    Returns:
        Dictionary with result, latency, cost
    """
    
    if decision.route == "cache":
        # CACHE ROUTE: Direct database lookup, no LLM
        tool_name = decision.tool
        
        if tool_name == "get_account_balance":
            result = MOCK_TOOLS["get_account_balance"](user_id)
        elif tool_name == "get_business_hours":
            result = MOCK_TOOLS["get_business_hours"]()
        elif tool_name == "greeting_response":
            result = MOCK_TOOLS["greeting_response"]()
        else:
            result = "Tool not found"
        
        return {
            "result": result,
            "route": "cache",
            "method": "Direct database lookup (no LLM)",
            "latency_ms": decision.latency_estimate,
            "cost_usd": decision.cost_estimate,
            "tool_used": tool_name
        }
    
    elif decision.route == "small_model":
        # SMALL MODEL ROUTE: Local model, cheap
        # In real system, would use DistilBERT or similar
        # For now, return mock response
        
        result = f"[Small Model Response for: {decision.intent}]"
        
        return {
            "result": result,
            "route": "small_model",
            "method": "Local quantized model (DistilBERT)",
            "latency_ms": decision.latency_estimate,
            "cost_usd": decision.cost_estimate,
            "model_used": "DistilBERT-quantized"
        }
    
    elif decision.route == "expensive_model":
        # EXPENSIVE MODEL ROUTE: Frontier LLM
        # In real system, would call OpenAI API
        # For now, return mock response
        
        result = f"[GPT-4o-mini Response for: {decision.intent}]"
        
        return {
            "result": result,
            "route": "expensive_model",
            "method": "Frontier LLM (GPT-4o-mini)",
            "latency_ms": decision.latency_estimate,
            "cost_usd": decision.cost_estimate,
            "model_used": "GPT-4o-mini"
        }


def calculate_savings(standard_cost: float, gatekeeper_cost: float) -> dict:
    """
    Calculate cost savings
    
    Args:
        standard_cost: Cost using standard "send everything to LLM" approach
        gatekeeper_cost: Cost using Gatekeeper routing
    
    Returns:
        Dictionary with savings metrics
    """
    
    savings_usd = standard_cost - gatekeeper_cost
    savings_percent = (savings_usd / standard_cost * 100) if standard_cost > 0 else 0
    
    return {
        "standard_cost": standard_cost,
        "gatekeeper_cost": gatekeeper_cost,
        "savings_usd": savings_usd,
        "savings_percent": savings_percent,
        "cost_reduction_ratio": standard_cost / gatekeeper_cost if gatekeeper_cost > 0 else float('inf')
    }