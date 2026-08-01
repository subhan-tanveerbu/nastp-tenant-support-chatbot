"""
config.py
---------
Handles application configuration:
- Loads environment variables from .env
- Loads the knowledge base file into memory once at startup

Keeping configuration in one place makes the rest of the app
easier to read and test.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from a local .env file (if present) into the environment.
load_dotenv()

# ----------------------------------------------------------------
# Environment variables
# ----------------------------------------------------------------
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

# ----------------------------------------------------------------
# File paths
# ----------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent
KNOWLEDGE_FILE_PATH: Path = BASE_DIR / "knowledge" / "nastp_info.txt"

# ----------------------------------------------------------------
# Fallback message used when the chatbot has no approved answer
# ----------------------------------------------------------------
FALLBACK_ANSWER: str = (
    "I don't have approved information about that. "
    "Please contact the NASTP support team."
)


def load_knowledge_base() -> str:
    """
    Read the knowledge base file from disk and return its contents
    as a single string.

    This function is meant to be called ONCE when the application
    starts (see app.py). The result should be cached in memory and
    reused for every request, rather than re-reading the file each time.

    Raises:
        FileNotFoundError: if the knowledge file does not exist.
        ValueError: if the knowledge file is empty.
    """
    if not KNOWLEDGE_FILE_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base file not found at: {KNOWLEDGE_FILE_PATH}"
        )

    content = KNOWLEDGE_FILE_PATH.read_text(encoding="utf-8").strip()

    if not content:
        raise ValueError("Knowledge base file is empty.")

    return content
