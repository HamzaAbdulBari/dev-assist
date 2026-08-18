"""Integration tests for Vector Retrieval (app.retrieval)."""

import pytest
from app.retrieval import retrieve


def test_retrieval_returns_chunks():
    """Verify that semantic search returns matching chunks for a relevant query."""
    results = retrieve(query="How to create a POST endpoint", top_k=3)

    assert isinstance(results, list)
    assert len(results) > 0

    first_result = results[0]
    assert "content" in first_result
    assert "source" in first_result
    assert "score" in first_result


def test_retrieval_respects_top_k():
    """Verify that the top_k parameter limits the number of returned chunks."""
    k = 2
    results = retrieve(query="FastAPI parameters", top_k=k)

    assert isinstance(results, list)
    assert len(results) <= k


def test_retrieval_contains_source_information():
    """Verify that source file paths are returned in retrieval results."""
    results = retrieve(query="dependency injection", top_k=3)

    assert len(results) > 0
    sources = [r["source"] for r in results]

    # At least one result should reference dependencies or tutorial documentation
    assert any("dependencies.md" in src or ".md" in src for src in sources)


def test_retrieval_empty_query():
    """Verify that an empty query string returns an empty list without querying db."""
    assert retrieve(query="") == []
    assert retrieve(query="   ") == []
