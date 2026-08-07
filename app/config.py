"""Application Configuration.

This module loads environment variables from a .env file and exposes
typed configuration constants used throughout the application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository (parent of the 'app' directory)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the .env file located at repository root
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Database settings
# SQLAlchemy connection string. We use psycopg (v3) as the driver: postgresql+psycopg://user:pass@host:port/dbname
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:Hamza123@localhost:5433/rag_db"
)

# Groq LLM settings
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

# Embedding model settings
# sentence-transformers/all-MiniLM-L6-v2 produces dense 384-dimensional embeddings
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIMENSION: int = 384

# RAG & Chunking settings
TOP_K: int = int(os.getenv("TOP_K", "5"))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))

# Documentation data directory
DATA_DIR: Path = BASE_DIR / "data" / "fastapi"
