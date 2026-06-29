"""
Embeddings module - converts text to vectors
"""

import time
import numpy as np
from fastembed import TextEmbedding
from backend.config import EMBEDDING_MODEL, SAMPLE_INTENTS

# Load the model once (happens automatically)
print("Loading embedding model... This takes 30 seconds first time")
embedding_model = TextEmbedding(model_name=EMBEDDING_MODEL)
print("✅ Model loaded!")


def embed_text(text: str) -> np.ndarray:
    """
    Convert a text string to an embedding (vector)
    
    Input: "What's my balance?"
    Output: [0.123, -0.456, 0.789, ...] (384 numbers)
    
    Args:
        text: The text to embed
        
    Returns:
        numpy array of embeddings
    """
    start = time.time()
    
    # FIX: FastEmbed returns a generator, convert to list then numpy array
    embeddings = list(embedding_model.embed(text))
    embedding_array = np.array(embeddings[0])  # Get first (and only) result
    
    latency = (time.time() - start) * 1000  # Convert to ms
    
    print(f"Embedded '{text[:30]}...' in {latency:.2f}ms")
    
    return embedding_array


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate similarity between two vectors (0 to 1)
    
    1.0 = identical
    0.5 = somewhat similar
    0.0 = completely different
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
        
    Returns:
        Similarity score (0 to 1)
    """
    # Normalize vectors
    vec1_norm = vec1 / np.linalg.norm(vec1)
    vec2_norm = vec2 / np.linalg.norm(vec2)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1_norm, vec2_norm)
    
    return float(similarity)


def embed_all_intents():
    """
    Pre-embed all sample intents
    
    Returns:
        Dictionary with intent embeddings
    """
    intent_embeddings = {}
    
    for intent_name, examples in SAMPLE_INTENTS.items():
        print(f"\nEmbedding intent: {intent_name}")
        
        embeddings_list = []
        for example in examples:
            embedding = embed_text(example)
            embeddings_list.append(embedding)
        
        # FIX: Convert list to numpy array before taking mean
        embeddings_array = np.array(embeddings_list)
        intent_embeddings[intent_name] = np.mean(embeddings_array, axis=0)
    
    return intent_embeddings


# Pre-load all intents when module starts
print("\nPre-computing intent embeddings...")
INTENT_EMBEDDINGS = embed_all_intents()
print("\n✅ All intent embeddings ready!")