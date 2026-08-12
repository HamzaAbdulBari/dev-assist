"""Documentation Ingestion Script.

Loads markdown documentation, chunks it, generates vector embeddings,
and stores everything in PostgreSQL using pgvector.

Usage:
    python scripts/ingest.py
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path so 'app' modules can be imported directly
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP  # noqa: E402
from app.database import init_db, SessionLocal  # noqa: E402
from app.models import Chunk  # noqa: E402
from app.ingestion import load_markdown_files, create_chunks  # noqa: E402
from app.embeddings import embed_texts  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ingest")


def run_ingestion() -> None:
    """Execute the full document ingestion pipeline."""
    logger.info("Initializing database and pgvector extension...")
    init_db()

    # Step 1: Load Markdown documents
    logger.info(f"Loading documents from: {DATA_DIR}")
    documents = load_markdown_files(DATA_DIR)
    if not documents:
        logger.warning("No markdown files found to ingest. Exiting.")
        return

    logger.info(f"Found {len(documents)} document(s).")

    # Step 2: Split documents into chunks
    logger.info(f"Creating chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
    chunks_data = create_chunks(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    if not chunks_data:
        logger.warning("No chunks were produced from documents. Exiting.")
        return

    logger.info(f"Total chunks created: {len(chunks_data)}")

    # Step 3: Generate vector embeddings
    logger.info("Generating embeddings for all chunks...")
    texts = [item["content"] for item in chunks_data]
    embeddings = embed_texts(texts)
    logger.info(f"Generated {len(embeddings)} embedding vectors.")

    # Step 4: Store chunks and embeddings in PostgreSQL
    logger.info("Storing chunks and embeddings in PostgreSQL...")
    db = SessionLocal()
    try:
        # Clear existing chunks so running ingestion is idempotent (avoids duplicates)
        deleted_count = db.query(Chunk).delete()
        if deleted_count > 0:
            logger.info(f"Cleared {deleted_count} existing chunk(s) from database.")

        # Prepare Chunk ORM objects
        db_chunks = []
        for i, item in enumerate(chunks_data):
            chunk_obj = Chunk(
                content=item["content"],
                source=item["source"],
                chunk_index=item["chunk_index"],
                embedding=embeddings[i]
            )
            db_chunks.append(chunk_obj)

        # Bulk insert chunks
        db.bulk_save_objects(db_chunks)
        db.commit()
        logger.info(f"Successfully stored {len(db_chunks)} chunks in PostgreSQL!")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to store chunks in database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_ingestion()
