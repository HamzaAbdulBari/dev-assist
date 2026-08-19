# Documentation RAG Assistant

A beginner-friendly, production-grounded Retrieval-Augmented Generation (RAG) assistant designed to answer technical questions accurately using documentation as its source of truth.

---

## Project Overview

The **Documentation RAG Assistant** enables users to query FastAPI documentation in natural language. Instead of relying on general LLM memory (which can hallucinate non-existent parameters or deprecated syntax), this system:
1. Translates the user's question into a numerical dense vector (embedding).
2. Performs vector similarity search via PostgreSQL and `pgvector` to identify the most relevant documentation chunks.
3. Formats an explicit prompt containing only the retrieved context chunks.
4. Uses Groq's high-speed inference running `qwen/qwen3.8-27b` to generate a factual answer strictly grounded in the retrieved documentation, accompanied by exact source references.

---

## Technology Stack

- **Language:** Python 3.13 / 3.12
- **Web Framework:** FastAPI & Uvicorn
- **Database & Vector Search:** PostgreSQL 18 with `pgvector` extension
- **Database ORM & Driver:** SQLAlchemy & `psycopg` (v3)
- **Local Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **LLM & Inference:** Groq Cloud API running `qwen/qwen3.8-27b`
- **Validation & Settings:** Pydantic v2 & `python-dotenv`
- **Web Interface:** HTML5, CSS3, Jinja2
- **Testing:** Pytest & HTTPX (`TestClient`)

---

## Architecture

The system follows a clean, decoupled RAG pipeline:

```text
Question
   ↓
Embedding (sentence-transformers)
   ↓
PostgreSQL + pgvector (Cosine Distance: <=>)
   ↓
Relevant Chunks (Top-K)
   ↓
Prompt Construction (Strict grounding instructions)
   ↓
Groq Qwen (High-speed LLM completion)
   ↓
Answer + Sources
```

---

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure PostgreSQL and pgvector

Ensure PostgreSQL is running with the `pgvector` extension installed. If using Docker, you can run:

```bash
docker run -d --name rag-postgres -p 5433:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=Hamza123 -e POSTGRES_DB=rag_db pgvector/pgvector:pg18
```

The application automatically executes `CREATE EXTENSION IF NOT EXISTS vector;` and creates the `chunks` table when initialized.

### 4. Configure Environment Variables (`.env`)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your parameters in `.env`:

```env
DATABASE_URL=postgresql+psycopg://postgres:Hamza123@localhost:5433/rag_db
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
TOP_K=5
CHUNK_SIZE=700
CHUNK_OVERLAP=100
```

---

## Ingestion

Ingest the Markdown documentation into PostgreSQL chunks and vector embeddings:

```bash
python scripts/ingest.py
```

This script:
1. Connects to PostgreSQL and verifies the `chunks` table and `vector` extension.
2. Recursively scans `data/fastapi/` for all `.md` files.
3. Splits files into overlapping chunks (~700 characters with 100-character overlap).
4. Generates 384-dimensional embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
5. Clears prior chunks and inserts the new records into PostgreSQL.

---

## Run

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --reload
```

- **Web Interface:** Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.
- **Interactive Swagger Docs:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- **Alternative ReDoc Docs:** Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc).

---

## Example

### Question:
```text
How do I create a POST endpoint in FastAPI?
```

### Answer:
```text
To create a POST endpoint in FastAPI, use the `@app.post()` decorator on your path operation function and declare a Pydantic model as a parameter to represent the request body.

Example:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
def create_item(item: Item):
    return item
```

### Sources:
- `tutorial/body.md`
- `tutorial/first-steps.md`

---

## Project Structure

```text
├── app/
│   ├── __init__.py      # Package marker
│   ├── config.py        # Centralized settings and environment variables
│   ├── database.py      # SQLAlchemy engine, session maker, and pgvector table initialization
│   ├── models.py        # ORM Chunk model with pgvector Vector(384) column
│   ├── schemas.py       # Pydantic request/response validation models
│   ├── ingestion.py     # Document loader and chunking algorithms
│   ├── embeddings.py    # Local sentence-transformers vector generation
│   ├── retrieval.py     # Cosine similarity search using pgvector
│   ├── generation.py    # Prompt builder and Groq LLM API invocation
│   ├── rag.py           # Orchestrates the end-to-end RAG flow
│   └── main.py          # FastAPI application, REST endpoints, and HTML UI
├── data/
│   └── fastapi/         # Sample Markdown documentation corpus
├── scripts/
│   └── ingest.py        # CLI script to load, chunk, embed, and store docs
├── templates/
│   └── index.html       # Jinja2 web interface for browser interaction
├── tests/
│   ├── test_ingestion.py # Tests document reading and chunk boundaries
│   ├── test_retrieval.py # Tests similarity retrieval and Top-K ranking
│   └── test_api.py       # Tests /health, /ask, and UI with mocked Groq
├── .env                 # Local environment secrets (not committed to git)
├── .env.example         # Template for environment configuration
├── .gitignore           # Git ignore patterns for venv, cache, and secrets
├── requirements.txt     # Python package dependencies
└── README.md            # Project documentation and guide
```
