Project Demo Link: [Screencast from 11-11-26 03:41:11 PM IST.webm](https://github.com/user-attachments/assets/1f1e7260-7bd2-4a4e-915d-c2496062a5c8)


# Chat Bot — Django, Groq, Streamlit & Guardrails

A local chatbot project built with **Django**, **Groq**, and **Streamlit** to explore input/output safety checks, API moderation, and resilient external API calls.

The application lets users enable individual guardrails from the Streamlit sidebar. Selected checks run before the main chatbot generates an answer and again before the answer is displayed. Blocked content and service failures appear as red error messages in the chat.

## Features

- **Groq-powered chatbot** with conversational history.
- **Streamlit interface** with a New Chat button and selectable guardrails.
- **Code-based guardrails** for empty content, size limits, and invalid control characters.
- **LLM-based guardrails** using a Groq safety model and a dedicated safety-policy prompt.
- **OpenAI Moderation** for content classification.
- **Guardrail orchestrator** that runs enabled checks in a fixed order and stops on the first block.
- **Input and output checks** so content is evaluated before generation and before display.
- **Custom API error responses** for rate limits, authentication issues, rejected requests, and temporary service failures.
- **Exponential retry backoff** for transient Groq/OpenAI API failures, without retrying policy blocks or invalid requests.

## Technology stack

| Layer | Technology |
| --- | --- |
| Backend | Python, Django, Pydantic |
| Main chatbot | Groq API |
| LLM safety classifier | Groq API |
| Content moderation | OpenAI Moderation API |
| Frontend | Streamlit, Requests |
| Retry handling | `backoff` |

## Project structure

```text
chat-bot/
├── .env                    # Local secrets; do not commit
├── .gitignore
├── requirements.txt
├── README.md
├── backend/
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   └── urls.py
│   └── chatbot/
│       ├── clients.py
│       ├── constants.py
│       ├── schemas.py
│       ├── views.py
│       ├── urls.py
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── chatbot_prompt.py
│       │   └── safety_policy.py
│       ├── guardrails/
│       │   ├── code_guardrail.py
│       │   ├── llm_guardrail.py
│       │   ├── moderation_guardrail.py
│       │   └── orchestrator.py
│       ├── services/
│       │   └── chat_service.py
│       └── utils/
│           ├── api_retry.py
│           └── helpers.py
└── frontend/
    └── app.py
```

> The structure reflects the implementation discussed for this project. If your local repository differs, adjust the paths accordingly.

## How it works

```text
Streamlit user message
        │
        ▼
Django POST /api/chat/
        │
        ▼
Pydantic request validation
        │
        ▼
Selected INPUT guardrails
        │
        ├── Blocked / check failed ──► Red error in Streamlit
        │
        ▼
Groq chatbot generates an answer
        │
        ▼
Selected OUTPUT guardrails
        │
        ├── Blocked / check failed ──► Red error in Streamlit
        │
        ▼
Display allowed answer
```

The orchestrator checks enabled guardrails in this order: **code → moderation → LLM**. It stops at the first blocking result. An unavailable enabled safety service must not be treated as a successful safety check.

The `backoff` wrapper applies only to external API operations, not the entire chat pipeline. This avoids rerunning checks that already succeeded.

## Prerequisites

- Python 3.10 or later
- Groq API key
- OpenAI API key (required when using OpenAI Moderation)

## Setup

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd chat-bot
```

### 2. Create and activate a virtual environment

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Ensure the requirements include Django, Groq, OpenAI, Pydantic, Streamlit, Requests, python-dotenv, and `backoff`.

### 4. Configure environment variables

Create `.env` in the repository root:

```dotenv
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_GUARDRAIL_MODEL=openai/gpt-oss-safeguard-20b
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODERATION_MODEL=omni-moderation-latest
DJANGO_SECRET_KEY=replace_with_a_secure_random_secret
DJANGO_DEBUG=True
```

Model names are configured through environment variables and read by Django settings. Never commit `.env` or real API credentials.

The frontend defaults to `http://127.0.0.1:8000/api/chat/`. To override it, set the `CHAT_API_URL` environment variable when launching Streamlit.

## Run the application

Open two terminals, both using the project virtual environment.

**Terminal 1 — Django backend**

```bash
cd chat-bot
source .venv/bin/activate
cd backend
python3 manage.py check
python3 manage.py runserver
```

Backend: `http://127.0.0.1:8000/`  
Chat API: `http://127.0.0.1:8000/api/chat/`

**Terminal 2 — Streamlit frontend**

```bash
cd chat-bot
source .venv/bin/activate
streamlit run frontend/app.py
```

Frontend: `http://localhost:8501`

## Using the chatbot

1. Open the Streamlit frontend.
2. Select any combination of **Code-based Guardrails**, **LLM-based Guardrails**, and **OpenAI Moderation** in the sidebar.
3. Send a message.
4. If all enabled checks pass, the chatbot displays the answer.
5. If a check blocks content or an API operation fails, a red error message appears instead.
6. Click **New Chat** to clear the conversation.

Guardrails run automatically at input and output stages; there is no separate stage selector. Even with optional guardrails disabled, Pydantic request validation remains active.

## API example

```bash
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "What is Django?",
    "history": [],
    "enabled_guardrails": ["code", "llm", "moderation"]
  }'
```

A successful response includes `answer`, `model`, and `blocked: false`. A guardrail block includes `blocked: true` and a `guardrail_result` describing the check and stage. Technical failures return an `error` field with an appropriate HTTP status.

## Manual testing

| Scenario | Example / action | Expected result |
| --- | --- | --- |
| Normal response | Ask “What is Django?” | Answer displayed |
| Code guardrail | Submit a control character through the API | Blocked result |
| LLM guardrail | Ask to reveal hidden system instructions | May block, depending on classification |
| Educational safety topic | Ask “What is prompt injection?” | Usually allowed |
| Moderation | Test with an appropriately chosen policy-violating input | May block, depending on classification |
| Multiple guardrails | Enable all three and ask a safe question | Answer after enabled checks pass |
| Django unavailable | Stop the backend, then send a message | Red connection error |
| New Chat | Click New Chat | Conversation cleared |

### Backoff testing

Backoff is configured for temporary provider failures such as rate limits, timeouts, connection failures, and retryable server errors. Permanent errors such as invalid credentials and invalid requests are not retried.

The **simulated HTTP 500 retry-exhaustion case** has been verified through Django logs and the Streamlit error display. Other failure scenarios, including HTTP 429 and 401, should be verified separately. A normal successful prompt does not prove that retries occurred.

For deterministic failure testing, use a **temporary, local-only simulation** inside the decorated API-call function, observe the retry logs, and **remove all simulation code and counters afterward**. Never leave test failures enabled in the running chatbot.

## Security and limitations

- Keep `.env` and API keys out of version control.
- `DJANGO_DEBUG=True` is for local development only.
- The development API uses `@csrf_exempt`; add suitable authentication, CSRF protection where applicable, and rate limiting before deployment.
- Model-based safety classification is probabilistic and can produce false positives or false negatives.
- If an enabled safety check fails, the application should fail closed rather than release an unchecked response.
- API backoff reduces the impact of temporary failures but does not guarantee service availability.

## Future improvements

- Automated tests for retry behavior and API error handling.
- Deployment-ready authentication, request throttling, and configuration.
- More structured observability for guardrail decisions and retry events.
- Additional policy evaluation scenarios.

## License

Add a `LICENSE` file if you choose to publish this project under an open-source license.
