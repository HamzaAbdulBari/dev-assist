"""Document Loading and Chunking.

This module handles loading Markdown documentation files from the file system
and splitting them into overlapping text chunks suitable for embedding and retrieval.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def extract_title(content: str) -> Optional[str]:
    """Extract a title from the first Markdown heading (# Heading) if present.

    Args:
        content: The raw text of the markdown document.

    Returns:
        The extracted title string, or None if no heading is found.
    """
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line.lstrip("#").strip()
    return None


def load_markdown_files(directory: Path | str) -> List[Dict[str, Any]]:
    """Recursively discover and load all Markdown (.md) files from a directory.

    Args:
        directory: Path to the directory containing documentation.

    Returns:
        A list of dictionaries, where each dictionary contains:
        - "source": Relative path to the file (e.g. "tutorial/first-steps.md")
        - "title": Extracted title or filename
        - "content": Cleaned text content of the file
    """
    base_path = Path(directory)
    if not base_path.exists():
        logger.warning(f"Documentation directory does not exist: {base_path}")
        return []

    documents: List[Dict[str, Any]] = []

    # rglob("*.md") recursively finds all files ending with .md
    for file_path in sorted(base_path.rglob("*.md")):
        if not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding="utf-8").strip()
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            continue

        # Skip completely empty files
        if not content:
            logger.info(f"Skipping empty markdown file: {file_path}")
            continue

        # Calculate a clean relative path for citation, e.g. "tutorial/first-steps.md"
        relative_source = file_path.relative_to(base_path).as_posix()
        title = extract_title(content) or file_path.stem.replace("-", " ").title()

        documents.append({
            "source": relative_source,
            "title": title,
            "content": content
        })

    logger.info(f"Loaded {len(documents)} markdown document(s) from {base_path}")
    return documents


def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 100) -> List[str]:
    """Split a string into overlapping chunks based on character count.

    Args:
        text: The input text to be split into chunks.
        chunk_size: Maximum target character size for each chunk.
        chunk_overlap: Number of characters to overlap between consecutive chunks.

    Returns:
        A list of text chunk strings.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: List[str] = []
    start = 0
    text_length = len(cleaned)

    # Step forward through the text with a sliding window
    step = chunk_size - chunk_overlap
    if step <= 0:
        step = chunk_size  # safety fallback in case overlap >= chunk_size

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start += step

    return chunks


def create_chunks(
    documents: List[Dict[str, Any]],
    chunk_size: int = 700,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """Process a list of loaded documents and split each into chunks with metadata.

    Args:
        documents: List of document dicts from `load_markdown_files`.
        chunk_size: Target size in characters for each chunk.
        chunk_overlap: Target overlap in characters.

    Returns:
        A list of chunk dicts, each with:
        - "source": Relative file path of the source document
        - "chunk_index": 0-indexed position within the document
        - "content": Text content of the chunk
    """
    all_chunks: List[Dict[str, Any]] = []

    for doc in documents:
        source = doc["source"]
        text_chunks = chunk_text(doc["content"], chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        for index, chunk in enumerate(text_chunks):
            all_chunks.append({
                "source": source,
                "chunk_index": index,
                "content": chunk
            })

    logger.info(f"Created {len(all_chunks)} chunk(s) from {len(documents)} document(s)")
    return all_chunks
