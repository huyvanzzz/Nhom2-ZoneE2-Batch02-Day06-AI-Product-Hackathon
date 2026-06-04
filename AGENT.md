# Agent Instructions

Repository: `VinM-Batch02-Day06-AI-Product-Hackathon`
Branch: `TranQuocKhanh_2A202600679`

## Purpose

This repo is the hackathon working tree for the Day 06 AI Product build. Keep changes focused on the current milestone and avoid broad refactors unless the plan explicitly requires them.

## Source of truth

- Read [`plan_v1.md`](plan_v1.md) before making implementation decisions.
- Use `spec/` for product requirements and `codebase/` for the prototype.
- Treat `hackathon-rules.md` as the delivery constraint document.

## Environment contract

- Use a dedicated Python virtual environment at `.venv/`.
- Do not commit `.env` or any secret values.
- Use the OpenAI-compatible gateway defined in `.env`:
  - `OPENAI_BASE_URL=http://localhost:20128/v1`
  - `OPENAI_MODEL=cx/gpt-5.4-mini`
- Load other external API credentials from `.env` only.

## Setup workflow

1. Create or activate `.venv/`.
2. Verify environment variables exist before running any agent code.
3. Keep dependencies isolated inside the virtual environment.
4. Add only the minimum files needed for the current milestone.

## Change policy

- Prefer small, reversible changes.
- Keep documentation concise and operational.
- If a file already exists for a purpose, update it instead of adding a duplicate.
- Avoid writing sample secrets into tracked files.

## Implementation notes

- If Python dependencies are added later, record them in the repository's dependency manifest before using them in code.
- If a new agent flow is introduced, document the required inputs, outputs, and failure mode in `codebase/README.md` or a nearby runbook.
