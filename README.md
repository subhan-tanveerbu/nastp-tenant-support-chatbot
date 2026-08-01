# NASTP Tenant Support Chatbot API

A lightweight, beginner-friendly backend API that answers approved tenant-facing questions for the **National Aerospace Science & Technology Park (NASTP)** digital platform. It uses a local text-based knowledge base and an OpenAI-compatible LLM (Groq API) — no vector databases, embeddings, or heavy AI frameworks required.

---

## 1. Project Overview

The NASTP Tenant Support Chatbot API is a simple FastAPI backend designed to answer tenant questions about onboarding, Expression of Interest (EOI), facilities, chapters, tenant services, FAQs, and contact information.

The chatbot answers **only** using information contained in a local knowledge file (`knowledge/nastp_info.txt`). If a question falls outside the approved knowledge base, the chatbot responds with a fixed, safe fallback message instead of guessing or hallucinating.

This project is intentionally lightweight so it can run comfortably on a low-end laptop, and is intended as a clean demonstration backend that frontend developers can integrate against.

---

## 2. Features

- Simple REST API built with FastAPI
- Local, file-based knowledge base (no database required)
- Knowledge base loaded once into memory at startup for speed
- OpenAI-compatible LLM integration (works with Groq's free API)
- Strict "no hallucination" system prompt design
- Clean separation of concerns (routes vs. business logic vs. config)
- Pydantic request/response validation
- Meaningful JSON error responses with correct HTTP status codes
- Auto-generated Swagger / OpenAPI documentation
- No LangChain, vector databases, embeddings, or heavy AI libraries

---

## 3. Technology Stack

| Component            | Technology              |
|-----------------------|--------------------------|
| Language              | Python 3.11+             |
| Web Framework         | FastAPI                  |
| ASGI Server           | Uvicorn                  |
| LLM Client            | OpenAI Python SDK (OpenAI-compatible) |
| LLM Provider          | Groq API (recommended, free tier) |
| Config Management     | python-dotenv             |
| Data Validation       | Pydantic                  |

---

## 4. Project Structure

```
nastp-chatbot/
│── app.py                  # FastAPI app, routes, request/response models
│── chatbot.py               # Core chatbot logic (LLM calls, prompt building)
│── config.py                 # Environment variables & knowledge base loader
│── requirements.txt          # Python dependencies
│── README.md                 # Project documentation (this file)
│── .env.example                # Example environment variable file
│
└── knowledge/
       └── nastp_info.txt        # Approved knowledge base content
```

---

## 5. Installation

Clone or download the project, then move into the project folder:

```bash
cd nastp-chatbot
```

---

## 6. Creating a Virtual Environment

It's recommended to use a virtual environment to keep dependencies isolated.

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 7. Installing Requirements

With the virtual environment activated, install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 8. Environment Variables

Copy the example environment file and fill in your own values:

```bash
cp .env.example .env
```

`.env` file contents:

| Variable         | Description                                          | Example                                |
|------------------|-------------------------------------------------------|-----------------------------------------|
| `GROQ_API_KEY`   | Your Groq API key (get one free at console.groq.com)   | `gsk_xxxxxxxxxxxxxxxxxxxx`               |
| `GROQ_BASE_URL`  | Base URL for the OpenAI-compatible Groq endpoint        | `https://api.groq.com/openai/v1`         |
| `MODEL_NAME`     | The model used to generate answers                     | `llama-3.3-70b-versatile`                |

> ⚠️ Never commit your real `.env` file or API key to version control.

---

## 9. Running the Server

Start the development server with auto-reload:

```bash
uvicorn app:app --reload
```

Or run directly with Python:

```bash
python app.py
```

By default, the server runs on `http://127.0.0.1:8000`.

---

## 10. Swagger Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **OpenAPI JSON schema:** `http://127.0.0.1:8000/openapi.json`

---

## 11. Local Development URLs

| Purpose        | URL                                    |
|-----------------|------------------------------------------|
| Root            | `http://127.0.0.1:8000/`                  |
| Health check    | `http://127.0.0.1:8000/health`             |
| Chat endpoint   | `http://127.0.0.1:8000/chat`                |
| Swagger docs    | `http://127.0.0.1:8000/docs`                 |

---

## 12. Production Deployment URL (Placeholder)

Replace this with your actual deployed URL once the API is live (e.g., on Vercel, Render, Railway, or a VPS):

**Base URL**

```
https://your-domain.vercel.app
```

All examples in this document use this placeholder — replace it with your real production URL when integrating on the frontend.

---

## 13. API Documentation

### 13.1 GET `/`

**Purpose:** Confirms that the API is running.

- **HTTP Method:** `GET`
- **Headers:** None required
- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:** None

**Success Response — `200 OK`**

```json
{
  "message": "NASTP Chatbot API Running"
}
```

**Error Responses:** None expected under normal operation.

**Example Request**

```bash
curl -X GET https://your-domain.vercel.app/
```

**Example Response**

```json
{
  "message": "NASTP Chatbot API Running"
}
```

---

### 13.2 GET `/health`

**Purpose:** Health check endpoint for uptime monitoring and load balancers.

- **HTTP Method:** `GET`
- **Headers:** None required
- **Request Body:** None
- **Path Parameters:** None
- **Query Parameters:** None

**Success Response — `200 OK`**

```json
{
  "status": "healthy"
}
```

**Error Responses:** None expected under normal operation.

**Example Request**

```bash
curl -X GET https://your-domain.vercel.app/health
```

**Example Response**

```json
{
  "status": "healthy"
}
```

---

### 13.3 POST `/chat`

**Purpose:** Sends a tenant's question to the chatbot and returns an answer based strictly on the approved knowledge base.

- **HTTP Method:** `POST`
- **Headers:**
  - `Content-Type: application/json`
- **Request Body:**

| Field      | Type   | Required | Description                          |
|------------|--------|----------|----------------------------------------|
| `question` | string | Yes      | The tenant's question (non-empty)       |

```json
{
  "question": "How do I become a tenant?"
}
```

- **Path Parameters:** None
- **Query Parameters:** None

**Success Response — `200 OK`**

```json
{
  "answer": "To become a NASTP tenant, you start by submitting an Expression of Interest (EOI), followed by a consultation, an offer letter, signing the tenancy agreement, and completing onboarding orientation."
}
```

**Error Responses**

| Status Code | Scenario                                   | Example Body |
|-------------|----------------------------------------------|----------------|
| `400 Bad Request` | Empty or whitespace-only question | `{"error": "Invalid request", "detail": "The 'question' field cannot be empty."}` |
| `422 Unprocessable Entity` | Malformed JSON body / missing `question` field | Standard FastAPI/Pydantic validation error |
| `500 Internal Server Error` | Missing API key or LLM call failure | `{"error": "Chatbot error", "detail": "Server misconfiguration: GROQ_API_KEY is missing. Please set it in your .env file."}` |
| `503 Service Unavailable` | Knowledge base failed to load at startup | `{"error": "Knowledge base unavailable", "detail": "Knowledge base file not found at: .../knowledge/nastp_info.txt"}` |

**Example Request**

```bash
curl -X POST https://your-domain.vercel.app/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I become a tenant?"}'
```

**Example Response**

```json
{
  "answer": "To become a NASTP tenant, you start by submitting an Expression of Interest (EOI)..."
}
```

**Example "Out of Scope" Response**

```json
{
  "answer": "I don't have approved information about that. Please contact the NASTP support team."
}
```

---

## 14. Integration Guide

This section explains exactly how a frontend should integrate with the API without needing to read the backend source code.

- **Endpoint to call:** `POST /chat`
- **HTTP Method:** `POST`
- **Required Headers:** `Content-Type: application/json`
- **Request JSON format:**
  ```json
  { "question": "string (required, non-empty)" }
  ```
- **Expected JSON response (success):**
  ```json
  { "answer": "string" }
  ```
- **Field to render:** Display the `answer` field as the chatbot's reply bubble in the UI.
- **Suggested loading state:** While waiting for the response, show a typing indicator or disabled input with a spinner (typical LLM responses take 1–4 seconds).
- **Suggested error handling:**
  - If the response status is not `200`, read the `error` and `detail` fields and show a friendly message such as: *"Sorry, something went wrong. Please try again."*
  - If the request times out or the network fails, show: *"Unable to reach the chatbot. Please check your connection."*
  - Always re-enable the input field after a response or error so the user can retry.

---

## 15. Example Fetch API Integration

```javascript
async function askChatbot(question) {
  const response = await fetch("https://your-domain.vercel.app/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong. Please try again.");
  }

  return data.answer;
}

// Usage
askChatbot("How do I become a tenant?")
  .then((answer) => console.log("Chatbot:", answer))
  .catch((err) => console.error("Error:", err.message));
```

---

## 16. Example Axios Integration

```javascript
import axios from "axios";

const API_BASE_URL = "https://your-domain.vercel.app";

async function askChatbot(question) {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, { question });
    return response.data.answer;
  } catch (error) {
    const message =
      error.response?.data?.detail || "Something went wrong. Please try again.";
    throw new Error(message);
  }
}

// Usage
askChatbot("What facilities are available?")
  .then((answer) => console.log("Chatbot:", answer))
  .catch((err) => console.error("Error:", err.message));
```

---

## 17. Example JavaScript Frontend Integration (Vanilla HTML/JS)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>NASTP Chatbot Demo</title>
</head>
<body>
  <input id="questionInput" type="text" placeholder="Ask a question..." />
  <button id="askButton">Ask</button>
  <p id="loadingText" style="display:none;">Loading...</p>
  <p id="answerText"></p>

  <script>
    const API_BASE_URL = "https://your-domain.vercel.app";

    const questionInput = document.getElementById("questionInput");
    const askButton = document.getElementById("askButton");
    const loadingText = document.getElementById("loadingText");
    const answerText = document.getElementById("answerText");

    askButton.addEventListener("click", async () => {
      const question = questionInput.value.trim();
      if (!question) return;

      loadingText.style.display = "block";
      answerText.textContent = "";
      askButton.disabled = true;

      try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || "Something went wrong.");
        }

        answerText.textContent = data.answer;
      } catch (error) {
        answerText.textContent = `Error: ${error.message}`;
      } finally {
        loadingText.style.display = "none";
        askButton.disabled = false;
      }
    });
  </script>
</body>
</html>
```

---

## 18. Example React Integration

```jsx
import { useState } from "react";

const API_BASE_URL = "https://your-domain.vercel.app";

export default function NastpChatbot() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const askChatbot = async () => {
    if (!question.trim()) return;

    setLoading(true);
    setError("");
    setAnswer("");

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Something went wrong. Please try again.");
      }

      setAnswer(data.answer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={askChatbot} disabled={loading}>
        {loading ? "Asking..." : "Ask"}
      </button>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {answer && <p>{answer}</p>}
    </div>
  );
}
```

---

## 19. Swagger URL

Once deployed, interactive API documentation is available at:

```
https://your-domain.vercel.app/docs
```

---

## 20. Deployment Notes

- Set `GROQ_API_KEY`, `GROQ_BASE_URL`, and `MODEL_NAME` as environment variables in your hosting provider's dashboard (never in source code).
- This app uses `uvicorn` as its ASGI server; most platforms (Render, Railway, Fly.io, a VPS) can run it directly with:
  ```bash
  uvicorn app:app --host 0.0.0.0 --port $PORT
  ```
- If deploying to a serverless platform such as Vercel, use an ASGI adapter/entry point compatible with that platform's Python runtime.
- Ensure the `knowledge/` folder is included in your deployment bundle — the app will fail to answer questions (returning `503`) if `nastp_info.txt` is missing.
- Enable CORS in `app.py` (via `fastapi.middleware.cors.CORSMiddleware`) if your frontend is hosted on a different domain than the API.

---

## 21. Future Improvements

- Add CORS middleware configuration for specific frontend domains
- Add rate limiting to prevent API abuse
- Add conversation history / multi-turn context support
- Add authentication (API keys or JWT) for production use
- Add automated tests (pytest) for routes and chatbot logic
- Support multiple knowledge base files organized by topic
- Add logging and request analytics

---

## 22. License

This project is provided as a demonstration template and may be used, modified, and distributed freely for educational and internal development purposes. Add a formal license (e.g., MIT) before public or commercial distribution.
