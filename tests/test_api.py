"""API Endpoint Integration and Unit Tests (app.main)."""

from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify that GET /health returns 200 and {'status': 'ok'}."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_endpoint_with_mocked_groq():
    """Verify that POST /ask returns answer and sources with Groq mocked."""
    mock_reply = "To create a POST endpoint in FastAPI, use the @app.post decorator."

    with patch("app.rag.generate_answer", return_value=mock_reply) as mock_llm:
        payload = {"question": "How do I create a POST endpoint in FastAPI?"}
        response = client.post("/ask", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["answer"] == mock_reply
        assert isinstance(data["sources"], list)
        assert len(data["sources"]) > 0
        assert any("body.md" in src or "first-steps.md" in src for src in data["sources"])

        # Ensure the mocked LLM was called exactly once with context
        mock_llm.assert_called_once()
        _, kwargs = mock_llm.call_args
        # kwargs or args contain question and context
        assert "question" in kwargs or len(mock_llm.call_args.args) >= 1


def test_ask_endpoint_empty_question():
    """Verify that POST /ask rejects an empty question with 422 or 400."""
    response = client.post("/ask", json={"question": ""})
    # Pydantic min_length=1 validator returns 422 Unprocessable Entity
    assert response.status_code in (400, 422)


def test_web_ui_get():
    """Verify GET / returns HTML template with page title."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Documentation Assistant" in response.text
    assert "<form" in response.text


def test_web_ui_post_with_mocked_groq():
    """Verify POST / handles form submissions and renders answer in HTML."""
    mock_reply = "A path parameter can be declared using {item_id} syntax."

    with patch("app.rag.generate_answer", return_value=mock_reply):
        response = client.post("/", data={"question": "How to declare path parameters?"})
        assert response.status_code == 200
        assert "Answer" in response.text
        assert mock_reply in response.text
        assert "path-params.md" in response.text
