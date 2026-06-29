"""
Configuration for Gatekeeper
"""

# Embeddings model
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"  # Fast, accurate, free

# Thresholds for routing decisions
CACHE_THRESHOLD = 0.85        # High confidence = use cache
SMALL_MODEL_THRESHOLD = 0.70  # Medium confidence = use small model

# Database
DATABASE_PATH = "data/queries.db"

# Sample intents (we'll use these for testing)
SAMPLE_INTENTS = {
    "account_lookup": [
        "What's my balance?",
        "Check my account",
        "How much do I have?",
        "Account status",
    ],
    "business_hours": [
        "What are your hours?",
        "When are you open?",
        "Business hours",
        "Store hours",
    ],
    "simple_calculation": [
        "What's 2+2?",
        "Calculate 5*3",
        "Math: 10-5",
    ],
    "greeting": [
        "Hello",
        "Hi there",
        "Hey",
        "Good morning",
    ],
}