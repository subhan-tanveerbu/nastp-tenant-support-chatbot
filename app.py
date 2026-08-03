"""
app.py
------
FastAPI application entry point for the NASTP Tenant Support Chatbot API.

Responsibilities:
- Define API routes (GET /, GET /health, POST /chat)
- Validate requests using Pydantic models
- Load the knowledge base once at startup
- Delegate chatbot logic to chatbot.py
- Return clean JSON responses with appropriate HTTP status codes
"""

from contextlib import asynccontextmanager
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import config
from chatbot import ChatbotError, get_answer

# ----------------------------------------------------------------
# In-memory state
# ----------------------------------------------------------------
# The knowledge base is loaded once when the app starts and reused
# for every request (see load_knowledge_base() in config.py).
app_state: dict = {"knowledge_base": None, "knowledge_error": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the knowledge base once when the application starts."""
    try:
        app_state["knowledge_base"] = config.load_knowledge_base()
        app_state["knowledge_error"] = None
    except (FileNotFoundError, ValueError) as exc:
        # Don't crash the app - store the error and surface it per-request
        # so the API can still respond with a meaningful message.
        app_state["knowledge_base"] = None
        app_state["knowledge_error"] = str(exc)

    yield  # App runs here

    # No teardown logic needed for this lightweight demo.


app = FastAPI(
    title="NASTP Tenant Support Chatbot API",
    description="A lightweight chatbot API answering approved NASTP tenant questions.",
    version="1.0.0",
    lifespan=lifespan,
)

# ----------------------------------------------------------------
# CORS Configuration
# ----------------------------------------------------------------

origins = [
    "https://nastp-delta.vercel.app",
    "http://localhost:3000",   # React (optional)
    "http://localhost:5173",   # Vite (optional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------------------------------------------------
# Pydantic models
# ----------------------------------------------------------------
class ChatRequest(BaseModel):
    """Request body for POST /chat"""

    question: str = Field(
        ...,
        min_length=1,
        description="The tenant's question in plain text.",
        examples=["How do I become a tenant?"],
    )


class ChatResponse(BaseModel):
    """Response body for POST /chat"""

    answer: str


class ErrorResponse(BaseModel):
    """Standard error response shape used across the API."""

    error: str
    detail: Optional[str] = None


# ----------------------------------------------------------------
# Routes
# ----------------------------------------------------------------
@app.get("/", tags=["General"])
def read_root() -> dict:
    """Basic liveness endpoint confirming the API is running."""
    return {"message": "NASTP Chatbot API Running"}


@app.get("/health", tags=["General"])
def health_check() -> dict:
    """Health check endpoint used for monitoring/uptime checks."""
    return {"status": "healthy"}


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    tags=["Chat"],
)
def chat(request: ChatRequest) -> JSONResponse:
    """
    Answer a tenant's question using only the local knowledge base,
    via an OpenAI-compatible LLM call (Groq).
    """
    question = request.question.strip()

    # ---- Validate input ----
    if not question:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid request",
                "detail": "The 'question' field cannot be empty.",
            },
        )

    # ---- Ensure knowledge base is available ----
    if app_state["knowledge_base"] is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Knowledge base unavailable",
                "detail": app_state["knowledge_error"]
                or "The knowledge base could not be loaded.",
            },
        )

    # ---- Call the chatbot ----
    try:
        answer = get_answer(question, app_state["knowledge_base"])
    except ChatbotError as exc:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Chatbot error", "detail": str(exc)},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"answer": answer},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
