# Environment Setup

This repo is meant to run with an isolated Python virtual environment and an OpenAI-compatible local gateway.

## Recommended setup

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## Environment variables

Create a local `.env` file with the following contract:

```ini
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=http://localhost:20128/v1
OPENAI_MODEL=cx/gpt-5.4-mini
FIRECRAWL_API_KEY=your_firecrawl_key_here
TAVILY_API_KEY=your_tavily_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```

## Notes

- Keep `.env` untracked.
- Use `.venv/` for all Python work in this repo.
- If a dependency list is added later, install it inside the active virtual environment only.
- The gateway URL and model name should stay fixed unless the build target changes.
