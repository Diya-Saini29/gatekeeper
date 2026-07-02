"""
Tool definitions and execution
"""

import json
from typing import Any, Dict
from datetime import datetime


class Tool:
    """Base tool class"""
    
    def __init__(self, name: str, description: str, execute_func):
        self.name = name
        self.description = description
        self.execute_func = execute_func
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with given parameters"""
        try:
            result = self.execute_func(**kwargs)
            return {
                "success": True,
                "tool": self.name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "success": False,
                "tool": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# ==================== MOCK TOOL IMPLEMENTATIONS ====================

def get_account_balance(user_id: str) -> str:
    """Get user's account balance"""
    # In real system, would query database
    # Mock data:
    mock_balances = {
        "user_123": 1234.56,
        "user_456": 5678.90,
        "user_789": 9876.54
    }
    balance = mock_balances.get(user_id, 0.00)
    return f"${balance:.2f}"


def get_business_hours() -> str:
    """Get business hours"""
    # Static data (doesn't change)
    return "9:00 AM - 5:00 PM, Monday-Friday"


def simple_calculator(expression: str) -> str:
    """Execute simple math expression"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


def greeting_response(name: str = "friend") -> str:
    """Return friendly greeting"""
    greetings = [
        f"Hello {name}! How can I help you today?",
        f"Hi {name}! What can I do for you?",
        f"Welcome {name}! How can I assist?",
    ]
    return greetings[0]  # Return first greeting


def search_documents(query: str, num_results: int = 3) -> str:
    """Search internal documents (RAG)"""
    # In real system, would search vector database
    mock_docs = {
        "AI": "AI is Artificial Intelligence...",
        "ML": "Machine Learning is a subset of AI...",
        "NLP": "Natural Language Processing handles text..."
    }
    
    results = []
    for key, doc in mock_docs.items():
        if key.lower() in query.lower():
            results.append(f"[{key}] {doc[:50]}...")
    
    return "\n".join(results) if results else "No documents found"


def get_weather(location: str) -> str:
    """Get weather for location"""
    # In real system, would call weather API
    mock_weather = {
        "delhi": "28°C, Partly cloudy",
        "mumbai": "32°C, Humid",
        "bangalore": "25°C, Rainy"
    }
    return mock_weather.get(location.lower(), "Weather data unavailable")


# ==================== TOOL REGISTRY ====================

TOOLS = {
    "get_account_balance": Tool(
        name="get_account_balance",
        description="Get user's account balance",
        execute_func=get_account_balance
    ),
    "get_business_hours": Tool(
        name="get_business_hours",
        description="Get business hours",
        execute_func=get_business_hours
    ),
    "simple_calculator": Tool(
        name="simple_calculator",
        description="Execute simple math expression",
        execute_func=simple_calculator
    ),
    "greeting_response": Tool(
        name="greeting_response",
        description="Return friendly greeting",
        execute_func=greeting_response
    ),
    "search_documents": Tool(
        name="search_documents",
        description="Search internal documents",
        execute_func=search_documents
    ),
    "get_weather": Tool(
        name="get_weather",
        description="Get weather for location",
        execute_func=get_weather
    ),
}


# ==================== TOOL SYNTHESIS ====================

class ToolSynthesizer:
    """Constructs tool calls without LLM"""
    
    @staticmethod
    def synthesize_tool_call(intent: str, query: str, user_id: str = "user_123") -> Dict[str, Any]:
        """
        Synthesize (construct) a tool call based on intent
        
        Args:
            intent: Classified intent
            query: Original user query
            user_id: User ID for personalization
        
        Returns:
            Tool call JSON
        """
        
        if intent == "account_lookup":
            # Construct: get_account_balance(user_id)
            return {
                "tool": "get_account_balance",
                "params": {"user_id": user_id},
                "method": "synthetic"
            }
        
        elif intent == "business_hours":
            # Construct: get_business_hours()
            return {
                "tool": "get_business_hours",
                "params": {},
                "method": "synthetic"
            }
        
        elif intent == "simple_calculation":
            # Extract expression from query
            # "Calculate 5*3" → extract "5*3"
            expressions = ["2+2", "5*3", "10-5", "100/2"]
            expression = None
            
            for expr in expressions:
                if expr in query:
                    expression = expr
                    break
            
            if not expression:
                # Fallback: try to find numbers and operators
                expression = query.split()[-1] if query.split() else "0"
            
            return {
                "tool": "simple_calculator",
                "params": {"expression": expression},
                "method": "synthetic"
            }
        
        elif intent == "greeting":
            # Construct: greeting_response()
            return {
                "tool": "greeting_response",
                "params": {"name": "friend"},
                "method": "synthetic"
            }
        
        else:
            # Unknown intent - need LLM
            return {
                "tool": None,
                "params": {},
                "method": "requires_llm",
                "reason": f"Cannot synthesize tool for intent: {intent}"
            }
    
    @staticmethod
    def execute_synthesized_call(tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a synthesized tool call
        
        Args:
            tool_call: Tool call JSON from synthesize_tool_call()
        
        Returns:
            Execution result
        """
        
        if tool_call["method"] == "requires_llm":
            return {
                "success": False,
                "reason": tool_call["reason"],
                "method": "requires_llm"
            }
        
        tool_name = tool_call["tool"]
        params = tool_call["params"]
        
        if tool_name not in TOOLS:
            return {
                "success": False,
                "error": f"Tool not found: {tool_name}"
            }
        
        tool = TOOLS[tool_name]
        result = tool.execute(**params)
        
        return result