"""Vector Retrieval Module.

Performs semantic search by computing cosine distance between the user's
question embedding and stored documentation chunk embeddings in PostgreSQL.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Chunk
from app.embeddings import embed_text
from app.config import TOP_K

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    top_k: int = TOP_K,
    db: Optional[Session] = None
) -> List[Dict[str, Any]]:
    """Retrieve the most relevant documentation chunks for a query.

    Args:
        query: The user's search query or question.
        top_k: Number of closest chunks to retrieve (defaults to TOP_K).
        db: Optional existing SQLAlchemy session. If None, a new session is created.

    Returns:
        List of dictionaries with keys: 'content', 'source', 'score'.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    # 1. Generate query embedding vector (length 384)
    query_vector = embed_text(cleaned_query)

    # Handle database session
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        # 2. Query PostgreSQL with pgvector
        # The cosine_distance method translates to the SQL operator <=>
        # Lower distance means higher semantic similarity.
        distance_col = Chunk.embedding.cosine_distance(query_vector).label("distance")

        stmt = (
            select(Chunk, distance_col)
            .order_by(distance_col.asc())
            .limit(top_k)
        )

        rows = db.execute(stmt).all()

        results: List[Dict[str, Any]] = []
        for chunk_row, distance in rows:
            # Cosine similarity is calculated as: 1 - cosine distance
            similarity_score = round(1.0 - float(distance), 4)
            results.append({
                "content": chunk_row.content,
                "source": chunk_row.source,
                "score": similarity_score
            })

        logger.info(f"Retrieved {len(results)} chunk(s) for query: '{cleaned_query}'")
        return results
    finally:
        if should_close:
            db.close()
