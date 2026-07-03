"""
Error handling and edge case management
"""

from typing import Dict, Any, Optional
from enum import Enum
import traceback
import logging
from datetime import datetime


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error type classifications"""
    EMBEDDING_ERROR = "embedding_error"
    CLASSIFICATION_ERROR = "classification_error"
    ROUTING_ERROR = "routing_error"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    API_ERROR = "api_error"
    TIMEOUT_ERROR = "timeout_error"
    VALIDATION_ERROR = "validation_error"
    DOCUMENT_ERROR = "document_error"
    UNKNOWN_ERROR = "unknown_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"           # Can retry immediately
    MEDIUM = "medium"     # Should try fallback
    HIGH = "high"         # Critical, user notification needed


class GatekeeperError(Exception):
    """Base exception for Gatekeeper system"""
    
    def __init__(self, error_type: ErrorType, message: str, 
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 recoverable: bool = True, context: Dict = None):
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.recoverable = recoverable
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "context": self.context,
            "timestamp": self.timestamp
        }


class ErrorHandler:
    """Handles errors and edge cases"""
    
    def __init__(self):
        self.error_log = []
        self.error_counts = {}
    
    def handle_embedding_error(self, query: str, original_error: Exception) -> Dict[str, Any]:
        """Handle embedding pipeline errors"""
        error = GatekeeperError(
            error_type=ErrorType.EMBEDDING_ERROR,
            message=f"Failed to embed query: {str(original_error)}",
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            context={"query": query, "original_error": str(original_error)}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "retry_with_fallback",
            "recommendation": "Query contains invalid characters. Retrying with sanitized input."
        }
    
    def handle_document_error(self, filename: str, original_error: Exception) -> Dict[str, Any]:
        """Handle document loading/processing errors"""
        error = GatekeeperError(
            error_type=ErrorType.DOCUMENT_ERROR,
            message=f"Failed to process document: {str(original_error)}",
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            context={"filename": filename}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "try_alternative_format",
            "recommendation": f"Could not process {filename}. Ensure file is valid PDF or TXT."
        }
    
    def handle_retrieval_error(self, query: str, original_error: Exception) -> Dict[str, Any]:
        """Handle RAG retrieval errors"""
        error = GatekeeperError(
            error_type=ErrorType.ROUTING_ERROR,
            message=f"Failed to retrieve documents: {str(original_error)}",
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            context={"query": query}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "escalate_to_llm",
            "recommendation": "Could not find relevant documents. Escalating to full LLM reasoning."
        }
    
    def handle_timeout_error(self, operation: str, timeout_ms: int) -> Dict[str, Any]:
        """Handle timeout errors"""
        error = GatekeeperError(
            error_type=ErrorType.TIMEOUT_ERROR,
            message=f"Operation '{operation}' timed out after {timeout_ms}ms",
            severity=ErrorSeverity.HIGH,
            recoverable=True,
            context={"operation": operation, "timeout_ms": timeout_ms}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "try_cached_response",
            "recommendation": "Operation took too long. Using cached response if available."
        }
    
    def handle_validation_error(self, field: str, value: Any, reason: str) -> Dict[str, Any]:
        """Handle input validation errors"""
        error = GatekeeperError(
            error_type=ErrorType.VALIDATION_ERROR,
            message=f"Validation failed for {field}: {reason}",
            severity=ErrorSeverity.LOW,
            recoverable=True,
            context={"field": field, "value": str(value), "reason": reason}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "sanitize_and_retry",
            "recommendation": f"Invalid input for {field}. Please provide valid input."
        }
    
    def handle_api_error(self, api_name: str, status_code: int, 
                        error_msg: str) -> Dict[str, Any]:
        """Handle external API errors"""
        error = GatekeeperError(
            error_type=ErrorType.API_ERROR,
            message=f"API {api_name} returned {status_code}: {error_msg}",
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            context={"api": api_name, "status_code": status_code}
        )
        
        self._log_error(error)
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "retry_with_backoff",
            "recommendation": f"API {api_name} unavailable. Retrying with exponential backoff."
        }
    
    def handle_unknown_error(self, original_error: Exception, 
                            context: Dict = None) -> Dict[str, Any]:
        """Handle unexpected errors"""
        error = GatekeeperError(
            error_type=ErrorType.UNKNOWN_ERROR,
            message=f"Unexpected error: {str(original_error)}",
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            context=context or {}
        )
        
        self._log_error(error)
        
        # Log full traceback for debugging
        logger.error(f"Unknown error: {traceback.format_exc()}")
        
        return {
            "status": "error",
            "error": error.to_dict(),
            "action": "escalate_to_support",
            "recommendation": "Unexpected error occurred. Please contact support."
        }
    
    def _log_error(self, error: GatekeeperError):
        """Log error and track statistics"""
        self.error_log.append(error)
        
        error_key = error.error_type.value
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log based on severity
        if error.severity == ErrorSeverity.HIGH:
            logger.error(f"[{error.error_type.value}] {error.message}")
        else:
            logger.warning(f"[{error.error_type.value}] {error.message}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = len(self.error_log)
        
        return {
            "total_errors": total_errors,
            "error_breakdown": self.error_counts,
            "recent_errors": [
                e.to_dict() for e in self.error_log[-5:]
            ]  # Last 5 errors
        }
    
    def clear_error_log(self):
        """Clear error log"""
        self.error_log.clear()
        self.error_counts.clear()


# ==================== INPUT VALIDATION ====================

class InputValidator:
    """Validates user inputs"""
    
    @staticmethod
    def validate_query(query: str) -> tuple:
        """
        Validate user query
        
        Returns: (is_valid, error_message)
        """
        # Check if query is empty
        if not query or len(query.strip()) == 0:
            return False, "Query cannot be empty"
        
        # Check query length (reasonable limits)
        if len(query) > 5000:
            return False, "Query is too long (max 5000 characters)"
        
        # Check for suspicious patterns
        if "<script>" in query.lower():
            return False, "Query contains invalid characters"
        
        # Query is valid
        return True, None
    
    @staticmethod
    def validate_user_id(user_id: str) -> tuple:
        """Validate user ID"""
        if not user_id:
            return False, "User ID cannot be empty"
        
        if len(user_id) > 100:
            return False, "User ID is too long"
        
        return True, None
    
    @staticmethod
    def validate_confidence(confidence: float) -> tuple:
        """Validate confidence score"""
        if not isinstance(confidence, (int, float)):
            return False, "Confidence must be a number"
        
        if confidence < 0 or confidence > 1:
            return False, "Confidence must be between 0 and 1"
        
        return True, None


# ==================== EDGE CASE HANDLING ====================

class EdgeCaseHandler:
    """Handles edge cases"""
    
    @staticmethod
    def handle_empty_query() -> Dict[str, Any]:
        """Handle empty query"""
        return {
            "status": "error",
            "error_type": "validation_error",
            "message": "Query cannot be empty",
            "suggestion": "Please provide a question or command"
        }
    
    @staticmethod
    def handle_very_long_query(query: str) -> str:
        """Handle very long query by truncating"""
        if len(query) > 5000:
            truncated = query[:5000]
            logger.warning(f"Query truncated from {len(query)} to {len(truncated)} chars")
            return truncated
        return query
    
    @staticmethod
    def handle_special_characters(query: str) -> str:
        """Handle queries with special characters"""
        # Sanitize but preserve meaning
        # Remove only truly problematic characters
        dangerous_chars = ['<', '>', '{', '}', '\\']
        sanitized = query
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        if sanitized != query:
            logger.warning(f"Query sanitized: removed special characters")
        
        return sanitized
    
    @staticmethod
    def handle_non_utf8() -> Dict[str, Any]:
        """Handle non-UTF8 encoding"""
        return {
            "status": "error",
            "error_type": "encoding_error",
            "message": "Query must be UTF-8 encoded",
            "suggestion": "Please provide input in UTF-8 format"
        }
    
    @staticmethod
    def handle_low_confidence(confidence: float) -> Dict[str, Any]:
        """Handle low confidence classification"""
        if confidence < 0.5:
            return {
                "status": "warning",
                "message": f"Low confidence ({confidence:.2f}) in classification",
                "action": "escalate_to_full_reasoning",
                "recommendation": "Query is ambiguous. Using full LLM reasoning."
            }
        return {}