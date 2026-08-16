"""FastAPI Application Main Entrypoint.

Exposes REST API endpoints and Jinja2 web interface for the Documentation Assistant:
- GET  /health : Health check
- POST /ask    : REST API for question answering
- GET  /        : Web interface
- POST /        : Web interface question submission
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import init_db
from app.schemas import HealthResponse, AskRequest, AskResponse
from app.rag import answer_question
from app.config import BASE_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure Jinja2 templates directory
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to initialize resources on startup."""
    logger.info("Initializing database schema on startup...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield


app = FastAPI(
    title="Documentation Assistant API",
    description="RAG-powered documentation assistant using FastAPI, pgvector, and Groq",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Simple health check endpoint returning status 'ok'."""
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AskResponse, tags=["RAG"])
def ask_question_endpoint(payload: AskRequest) -> AskResponse:
    """Submit a question to the RAG pipeline and receive an answer with source citations.

    Args:
        payload: AskRequest containing 'question' string.

    Returns:
        AskResponse with 'answer' string and 'sources' list.
    """
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    logger.info(f"Received question via /ask: '{question}'")
    try:
        result = answer_question(question)
        return AskResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse, tags=["Web UI"])
def get_ui(request: Request):
    """Render the simple search UI."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "question": "",
            "answer": None,
            "sources": []
        }
    )


@app.post("/", response_class=HTMLResponse, tags=["Web UI"])
async def post_ui(request: Request):
    """Handle question submission from the web UI form."""
    form_data = await request.form()
    question = form_data.get("question", "").strip()

    if not question:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "question": "",
                "answer": "Please enter a question to search.",
                "sources": []
            }
        )

    logger.info(f"Received question from Web UI: '{question}'")
    try:
        result = answer_question(question)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "question": question,
                "answer": result["answer"],
                "sources": result["sources"]
            }
        )
    except Exception as e:
        logger.error(f"Error processing question in Web UI: {e}")
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "question": question,
                "answer": f"An error occurred: {e}",
                "sources": []
            }
        )
