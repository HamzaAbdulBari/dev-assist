"""Answer Generation using Groq LLM.

Constructs the prompt with retrieved documentation context and queries
the Groq API running Qwen (or configured model).
"""

import logging
from typing import Optional
from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)

# Master prompt template required by specifications
PROMPT_TEMPLATE = """You are a documentation assistant.

Answer the user's question using only the provided documentation.

If the documentation does not contain enough information to answer the question,
say that you could not find the answer in the provided documentation.

Do not invent APIs, parameters, configuration values, or examples.

Documentation:

{context}

Question:

{question}
"""


def build_prompt(question: str, context: str) -> str:
    """Format the master prompt with context and the user question.

    Args:
        question: The user's question.
        context: Concatenated text of retrieved documentation chunks.

    Returns:
        Formatted prompt string.
    """
    return PROMPT_TEMPLATE.format(context=context.strip(), question=question.strip())


def generate_answer(
    question: str,
    context: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    """Call the Groq API to generate an answer based strictly on the retrieved context.

    Args:
        question: User query.
        context: Retrieved documentation text chunks combined.
        api_key: Optional Groq API key override. Defaults to GROQ_API_KEY.
        model: Optional model name override. Defaults to GROQ_MODEL.

    Returns:
        The generated text response.
    """
    effective_key = api_key or GROQ_API_KEY
    if not effective_key or effective_key == "your_groq_api_key_here":
        raise ValueError(
            "GROQ_API_KEY is not configured. Please set your GROQ_API_KEY in the .env file."
        )

    effective_model = model or GROQ_MODEL
    prompt = build_prompt(question=question, context=context)

    logger.info(f"Generating answer using Groq model: '{effective_model}'...")

    try:
        client = Groq(api_key=effective_key)
        chat_completion = client.chat.completions.create(
            model=effective_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.2,  # Low temperature for factual, grounded answers
        )

        answer = chat_completion.choices[0].message.content or ""
        return answer.strip()
    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        raise RuntimeError(f"Groq API error: {e}") from e
