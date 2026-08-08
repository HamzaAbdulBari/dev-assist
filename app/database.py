"""Database Connection and Session Management.

This module initializes the SQLAlchemy engine and session factory,
and ensures the pgvector extension is enabled in PostgreSQL.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import DATABASE_URL

# create_engine establishes the connection pool to PostgreSQL.
# echo=False keeps the console clean; set echo=True if you want to see all generated SQL.
engine = create_engine(DATABASE_URL, echo=False)

# sessionmaker creates a factory for new database sessions.
# autocommit=False ensures transactions are explicitly committed.
# autoflush=False prevents automatic flush of queries before commits.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that our ORM models (tables) inherit from.
Base = declarative_base()


def init_db() -> None:
    """Ensure the pgvector extension and database tables exist."""
    with engine.connect() as connection:
        # PostgreSQL extension 'vector' allows storing and querying vector embeddings
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        connection.commit()

    # Import models here so Base knows about the registered tables
    from app import models  # noqa: F401

    # Create all tables declared with Base (in our case, the 'chunks' table)
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency helper to provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
