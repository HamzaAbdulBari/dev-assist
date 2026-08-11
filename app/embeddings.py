"""Embedding Generation.

Generates dense vector representations of text using the local
sentence-transformers/all-MiniLM-L6-v2 model.
"""

import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

# Global cache for the embedding model so it only loads into memory once
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """Load and return the cached SentenceTransformer model instance.

    Returns:
        The initialized SentenceTransformer model.
    """
    global _model
    if _model is None:
        logger.info(f"Loading embedding model: '{EMBEDDING_MODEL}'...")
        try:
            # Attempt loading directly from local Hugging Face cache (fast & offline)
            _model = SentenceTransformer(EMBEDDING_MODEL, local_files_only=True)
        except Exception:
            # Fall back to remote download if not cached yet
            _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info("Embedding model loaded successfully.")
    return _model


def embed_text(text: str) -> List[float]:
    """Generate a vector embedding for a single string (e.g. user question).

    Args:
        text: The string to embed.

    Returns:
        A list of floats representing the embedding vector (length 384).
    """
    model = get_embedding_model()
    # encode() converts the text string into high-dimensional numerical coordinates
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate vector embeddings for a list of strings in batch.

    Args:
        texts: A list of text chunks to embed.

    Returns:
        A list of vector embeddings, each being a list of floats.
    """
    if not texts:
        return []

    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return [vec.tolist() for vec in embeddings]
