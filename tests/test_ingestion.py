"""Unit tests for Document Loading and Chunking (app.ingestion)."""

import pytest
from pathlib import Path
from app.ingestion import load_markdown_files, chunk_text, create_chunks, extract_title


def test_extract_title():
    """Verify title is extracted from the first '# Title' markdown heading."""
    md = "# First Steps in FastAPI\n\nSome introductory content."
    assert extract_title(md) == "First Steps in FastAPI"

    # Document with no header should return None
    md_no_header = "Just a paragraph without headers."
    assert extract_title(md_no_header) is None


def test_load_markdown_files_and_empty_files(tmp_path: Path):
    """Test that markdown files are loaded and empty files are skipped gracefully."""
    # Create valid markdown file
    valid_file = tmp_path / "valid.md"
    valid_file.write_text("# Valid Title\n\nFastAPI is a modern web framework.", encoding="utf-8")

    # Create empty markdown file
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("", encoding="utf-8")

    # Create whitespace-only markdown file
    whitespace_file = tmp_path / "whitespace.md"
    whitespace_file.write_text("   \n\n  ", encoding="utf-8")

    # Create non-markdown file
    other_file = tmp_path / "readme.txt"
    other_file.write_text("Plain text", encoding="utf-8")

    docs = load_markdown_files(tmp_path)

    # Only valid.md should be loaded
    assert len(docs) == 1
    assert docs[0]["source"] == "valid.md"
    assert docs[0]["title"] == "Valid Title"
    assert "FastAPI is a modern web framework." in docs[0]["content"]


def test_chunk_text():
    """Test text chunking and overlap logic."""
    text = "Word " * 200  # 1000 characters
    chunks = chunk_text(text, chunk_size=300, chunk_overlap=50)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 300

    # Test empty text
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_create_chunks():
    """Test creating structured chunks from document dictionaries."""
    sample_docs = [
        {
            "source": "tutorial/first-steps.md",
            "title": "First Steps",
            "content": "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        }
    ]

    chunks = create_chunks(sample_docs, chunk_size=30, chunk_overlap=5)

    assert len(chunks) >= 2
    assert chunks[0]["source"] == "tutorial/first-steps.md"
    assert chunks[0]["chunk_index"] == 0
    assert "content" in chunks[0]
