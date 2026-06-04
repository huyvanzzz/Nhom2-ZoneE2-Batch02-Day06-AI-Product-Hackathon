## Plan V1

Core bootstrap plan for `TranQuocKhanh_2A202600679`.

### Objective

Set up a clean, isolated development baseline for the hackathon prototype so the next build stage can use:

- an OpenAI-compatible gateway at `http://localhost:20128/v1`
- model `cx/gpt-5.4-mini`
- external API keys loaded from `.env`
- a dedicated virtual environment to avoid local conflicts

### Repo contract

- `spec/` holds the product specification and supporting evidence.
- `codebase/` holds the prototype implementation.
- root files document setup, rules, and agent instructions.

### Environment contract

Required variables:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL=http://localhost:20128/v1`
- `OPENAI_MODEL=cx/gpt-5.4-mini`
- `FIRECRAWL_API_KEY`
- `TAVILY_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

### Bootstrap milestones

1. Create and document the environment baseline.
2. Keep secrets in `.env` only; publish `.env.example` for shape only.
3. Use `.venv/` for all future Python work.
4. Add the first agent/prototype implementation after setup is stable.

### Working rule

Before coding the prototype, always check this file first and confirm the environment contract still matches the current build target.

### Backend v1 slice

- Backend v1 is a single FastAPI service under `codebase/backend`.
- The AI-assisted flow is: validate request, search, scrape, answer, notify.
- TDD is mandatory for all new runtime behavior: write a failing test, make it pass, then refactor only while tests stay green.
- Runtime entrypoint: `vinm_backend.main:app`.
