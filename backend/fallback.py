"""
Fallback system - gracefully handle errors and degradation
"""

from typing import Dict, Any, Optional
import time
from backend.embeddings import embed_text, cosine_similarity, INTENT_EMBEDDINGS
from backend.routing_engine import decide_route, execute_route
from backend.tools import ToolSynthesizer


class FallbackSystem:
    """
    Handles routing failures by trying alternative routes
    
    Priority order:
    1. Try Route 1 (Cache/Synthesized) - fastest, cheapest
    2. Try Route 2 (Small Model) - fast, cheap
    3. Try Route 3 (Expensive Model) - slow, expensive, best quality
    4. Return error message if all fail
    """
    
    def __init__(self):
        self.max_retries = 3
        self.route_priority = ["cache", "small_model", "expensive_model"]
    
    def process_query(self, query: str, user_id: str = "user_123") -> Dict[str, Any]:
        """
        Process a query with fallback logic
        
        Args:
            query: User query
            user_id: User ID
        
        Returns:
            Result dictionary with fallback information
        """
        
        start_time = time.time()
        attempt = 0
        last_error = None
        
        # Step 1: Embed and classify
        try:
            query_embedding = embed_text(query)
            
            scores = {}
            for intent_name, intent_embedding in INTENT_EMBEDDINGS.items():
                score = cosine_similarity(query_embedding, intent_embedding)
                scores[intent_name] = score
            
            best_intent = max(scores.items(), key=lambda x: x[1])
            intent = best_intent[0]
            confidence = best_intent[1]
            
        except Exception as e:
            return self._create_error_response(
                query, "Classification failed", str(e), 
                start_time
            )
        
        # Step 2: Try routing with fallback
        for route_preference in self.route_priority:
            attempt += 1
            
            try:
                # Make routing decision
                decision = decide_route(intent, confidence)
                
                # Try cache route first (synthesized)
                if route_preference == "cache" and decision.route == "cache":
                    result = self._try_cache_route(decision, query, user_id)
                    if result["success"]:
                        return self._create_success_response(
                            query, result, intent, confidence, 
                            decision.route, attempt, start_time
                        )
                    else:
                        last_error = result.get("error", "Cache execution failed")
                
                # Try small model route
                elif route_preference == "small_model":
                    result = self._try_small_model_route(decision, query)
                    if result["success"]:
                        return self._create_success_response(
                            query, result, intent, confidence, 
                            "small_model", attempt, start_time
                        )
                    else:
                        last_error = result.get("error", "Small model failed")
                
                # Try expensive model (fallback)
                elif route_preference == "expensive_model":
                    result = self._try_expensive_model_route(decision, query)
                    if result["success"]:
                        return self._create_success_response(
                            query, result, intent, confidence, 
                            "expensive_model", attempt, start_time
                        )
                    else:
                        last_error = result.get("error", "Expensive model failed")
            
            except Exception as e:
                last_error = f"Route {route_preference} failed: {str(e)}"
                continue
        
        # All routes failed
        return self._create_error_response(
            query, "All routing attempts failed", last_error, start_time
        )
    
    def _try_cache_route(self, decision, query: str, user_id: str) -> Dict[str, Any]:
        """Try to execute via cache (synthesized tool call)"""
        try:
            tool_call = ToolSynthesizer.synthesize_tool_call(
                decision.intent, query, user_id
            )
            
            if tool_call["method"] == "requires_llm":
                return {"success": False, "error": "Cannot synthesize this intent"}
            
            result = ToolSynthesizer.execute_synthesized_call(tool_call)
            return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _try_small_model_route(self, decision, query: str) -> Dict[str, Any]:
        """Try to execute via small model"""
        try:
            # Mock small model execution
            return {
                "success": True,
                "tool": "small_model",
                "result": f"[Small Model Response to: {query[:30]}...]",
                "latency_ms": 100,
                "cost_usd": 0.00001
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _try_expensive_model_route(self, decision, query: str) -> Dict[str, Any]:
        """Try to execute via expensive model (LLM)"""
        try:
            # Mock expensive model execution
            return {
                "success": True,
                "tool": "expensive_model",
                "result": f"[GPT-4o-mini Response to: {query}]",
                "latency_ms": 2000,
                "cost_usd": 0.001
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_success_response(self, query: str, result: Dict, 
                                intent: str, confidence: float,
                                route: str, attempts: int,
                                start_time: float) -> Dict[str, Any]:
        """Create success response"""
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "status": "success",
            "query": query,
            "result": result["result"],
            "intent": intent,
            "confidence": confidence,
            "route_used": route,
            "attempts_needed": attempts,
            "total_latency_ms": total_latency,
            "cost_usd": result.get("cost_usd", 0.0),
            "fallback_used": attempts > 1
        }
    
    def _create_error_response(self, query: str, error_type: str, 
                              error_msg: str, start_time: float) -> Dict[str, Any]:
        """Create error response"""
        total_latency = (time.time() - start_time) * 1000
        
        return {
            "status": "error",
            "query": query,
            "error_type": error_type,
            "error_message": error_msg,
            "total_latency_ms": total_latency,
            "fallback_exhausted": True,
            "recommendation": "Please try again later or contact support"
        }