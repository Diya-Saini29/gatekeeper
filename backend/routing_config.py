"""
Routing configuration and decision logic
"""

# Routing thresholds
THRESHOLDS = {
    "cache": 0.85,           # High confidence = use cache
    "small_model": 0.70,     # Medium confidence = use small model
    "expensive_model": 0.0   # Low confidence = use expensive model
}

# Complexity scoring for different intents
INTENT_COMPLEXITY = {
    "account_lookup": 0.1,           # Very simple (just database lookup)
    "business_hours": 0.1,           # Very simple (static data)
    "simple_calculation": 0.2,       # Simple (basic math)
    "greeting": 0.05,                # Extremely simple (predefined responses)
    "unknown": 1.0                   # Complex (needs reasoning)
}

# Route costs (in USD)
ROUTE_COSTS = {
    "cache": 0.0,            # Free
    "small_model": 0.00001,  # 0.001 cents per query
    "expensive_model": 0.001 # 0.1 cents per query
}

# Route latencies (in milliseconds)
ROUTE_LATENCIES = {
    "cache": 5,              # Instant database lookup
    "small_model": 100,      # Local model inference
    "expensive_model": 2000  # API call to OpenAI
}

# Mock tool responses (simulating what tools return)
MOCK_TOOLS = {
    "get_account_balance": lambda user_id: f"${1234.56}",
    "get_business_hours": lambda: "9:00 AM - 5:00 PM, Mon-Fri",
    "simple_calculator": lambda expr: str(eval(expr)),
    "greeting_response": lambda: "Hello! How can I help you today?"
}

# Intent to tool mapping
INTENT_TO_TOOL = {
    "account_lookup": "get_account_balance",
    "business_hours": "get_business_hours",
    "simple_calculation": "simple_calculator",
    "greeting": "greeting_response"
}