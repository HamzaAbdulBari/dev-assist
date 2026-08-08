"""SQLAlchemy Database Models.

Defines the database schema for storing text chunks and their vector embeddings.
"""

from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from app.database import Base
from app.config import EMBEDDING_DIMENSION


class Chunk(Base):
    """Represents a chunk of documentation text stored in the database.

    Attributes:
        id: Unique identifier for the chunk (Primary Key).
        content: The actual text content extracted from documentation.
        source: Relative file path of the source markdown document.
        chunk_index: The sequential index of this chunk within its source file.
        embedding: Vector representation of the content (384 dimensions for all-MiniLM-L6-v2).
    """
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(Text, nullable=False)
    source = Column(String(500), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    embedding = Column(Vector(EMBEDDING_DIMENSION), nullable=False)

    def __repr__(self) -> str:
        return f"<Chunk id={self.id} source='{self.source}' chunk_index={self.chunk_index}>"
