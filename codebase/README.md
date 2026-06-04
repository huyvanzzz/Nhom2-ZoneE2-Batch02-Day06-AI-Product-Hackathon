# Codebase

This folder contains the prototype code for the hackathon project.

## Backend v1 requirement

The current prototype lives in `codebase/backend` and is organized as a single FastAPI service.

Required runtime contract:

- Python 3.11+
- a local virtual environment at `./.venv`
- OpenAI-compatible gateway at `http://localhost:20128/v1`
- model name `cx/gpt-5.4-mini`
- external API keys loaded from `.env`

## Setup

1. Create or activate the root virtual environment.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

2. Install backend dependencies.

```powershell
cd codebase/backend
..\..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

3. Run tests.

```powershell
..\..\.venv\Scripts\python.exe -m pytest -v
```

4. Start the API.

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn vinm_backend.main:app --reload
```

## External tools

The backend is wired to these external services:

- OpenAI-compatible gateway for answer generation
- Tavily for search
- Firecrawl for page retrieval
- Telegram for notifications

## Day 6 demo flow

- `POST /chat/session`
- `POST /chat/message`
- `GET /chat/session/{session_id}/messages`
- `GET /cases/{case_id}`
- `PATCH /cases/{case_id}`
- `POST /booking/draft`
- `GET /booking/{booking_id}`
- `PATCH /booking/{booking_id}`
- `GET /doctor/cases`
- `GET /doctor/cases/{case_id}`
- `POST /doctor/cases/{case_id}/notes`
- `PATCH /doctor/cases/{case_id}/status`
- `GET /debug/cases/{case_id}/logs`

## Demo payloads

```powershell
$session = Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/session

Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/message `
  -ContentType "application/json" `
  -Body (@{ session_id=$session.session_id; content="Toi dau da day, day hoi kho tieu 2 tuan nay." } | ConvertTo-Json)

Invoke-RestMethod -Method Post http://127.0.0.1:8000/chat/message `
  -ContentType "application/json" `
  -Body (@{ session_id=$session.session_id; content="Me toi 58 tuoi, dau vua." } | ConvertTo-Json)

Invoke-RestMethod http://127.0.0.1:8000/doctor/cases
```

## Notes

- Do not commit `.env` or any secret values.
- Keep all Python work inside `.venv`.
- If you add new runtime behavior, add tests first and keep the runbook in sync.
