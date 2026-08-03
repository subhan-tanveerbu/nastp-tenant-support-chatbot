"""
chatbot.py
----------
Core chatbot logic, kept separate from the FastAPI routes in app.py.

Responsibilities:
- Build the system prompt that constrains the LLM to the knowledge base
- Call the OpenAI-compatible Groq API
- Return a clean, safe answer string
"""

from openai import OpenAI, APIError, APIConnectionError, AuthenticationError

import config
from retriever import retrieve
# System prompt template that instructs the LLM to stay strictly
# within the bounds of the supplied knowledge base.
SYSTEM_PROMPT_TEMPLATE = """You are the official NASTP Tenant Support Chatbot.

Only answer using the provided knowledge.
If the answer does not exist inside the knowledge, clearly state that you don't know.
Do not guess.
Do not make assumptions.
Keep answers concise, professional and friendly.

Knowledge:
{knowledge}
"""


class ChatbotError(Exception):
    """Raised when the chatbot cannot produce an answer due to a backend issue."""


def _build_client() -> OpenAI:
    """
    Create an OpenAI-compatible client pointed at the Groq API.

    Raises:
        ChatbotError: if the API key is missing.
    """
    if not config.GROQ_API_KEY:
        raise ChatbotError(
            "Server misconfiguration: GROQ_API_KEY is missing. "
            "Please set it in your .env file."
        )

    return OpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)


def get_answer(question: str, knowledge_base: str) -> str:
    """
    Send the user's question to the LLM, constrained to the given
    knowledge base, and return the chatbot's answer.

    Args:
        question: The tenant's question (already validated as non-empty).
        knowledge_base: The full contents of nastp_info.txt, loaded once
            at startup and passed in by the caller.

    Returns:
        The chatbot's answer as plain text.

    Raises:
        ChatbotError: if the API key is missing or the LLM call fails.
    """
    client = _build_client()

    relevant_knowledge = retrieve(question)

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
    knowledge=relevant_knowledge
    )

    try:
        response = client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question:\n{question}"},
            ],
            temperature=0.2,
            max_tokens=500,
        )
    except Exception as exc:
        raise ChatbotError(f"LLM Error: {str(exc)}") from exc

    answer = response.choices[0].message.content

    if not answer or not answer.strip():
        return config.FALLBACK_ANSWER

    return answer.strip()
