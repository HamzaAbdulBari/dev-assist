"""Core RAG (Retrieval-Augmented Generation) Pipeline.

Connects vector retrieval and LLM generation into a single end-to-end function:
answer_question(question)
"""

import logging
from typing import Dict, Any, List
from app.retrieval import retrieve
from app.generation import generate_answer
from app.config import TOP_K

logger = logging.getLogger(__name__)


def answer_question(question: str, top_k: int = TOP_K) -> Dict[str, Any]:
    """Execute the end-to-end RAG pipeline for a given question.

    Flow:
        1. Clean and validate the input question.
        2. Retrieve top-K relevant documentation chunks from PostgreSQL.
        3. If no relevant chunks are found, return a polite default message.
        4. Assemble the retrieved chunks into a context block.
        5. Pass the question and context to Groq (Qwen model) for answer generation.
        6. Extract unique sources and return the answer and source list.

    Args:
        question: The user query string.
        top_k: Maximum number of chunks to retrieve.

    Returns:
        A dict with:
        - "answer": LLM generated response string.
        - "sources": Unique list of source file paths used.
    """
    cleaned_question = question.strip()
    if not cleaned_question:
        return {
            "answer": "Please provide a valid, non-empty question.",
            "sources": []
        }

    logger.info(f"Processing question: '{cleaned_question}'")

    # Step 1 & 2: Retrieve relevant chunks via semantic search
    chunks = retrieve(query=cleaned_question, top_k=top_k)

    if not chunks:
        logger.warning("No relevant documentation chunks were retrieved.")
        return {
            "answer": "I could not find any relevant documentation to answer your question.",
            "sources": []
        }

    # Step 3: Combine retrieved chunk contents into a single context string
    context_blocks = []
    for chunk in chunks:
        context_blocks.append(f"--- Source: {chunk['source']} ---\n{chunk['content']}")
    context_text = "\n\n".join(context_blocks)

    # Step 4: Call Groq to generate the answer strictly based on the context
    try:
        answer = generate_answer(question=cleaned_question, context=context_text)
    except ValueError as e:
        logger.warning(f"Groq API key configuration issue: {e}")
        answer = f"Configuration Notice: {e}"
    except Exception as e:
        logger.error(f"Error during LLM answer generation: {e}")
        answer = f"An error occurred while generating the answer: {e}"

    # Step 5: Collect unique sources in the order they were retrieved
    unique_sources: List[str] = []
    seen = set()
    for chunk in chunks:
        source = chunk["source"]
        if source not in seen:
            seen.add(source)
            unique_sources.append(source)

    return {
        "answer": answer,
        "sources": unique_sources
    }
