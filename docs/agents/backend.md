# Backend

## Stack
- Language / framework: Python 3.12, FastAPI, Pydantic v2, httpx (async), APScheduler
  (`AsyncIOScheduler`), SQLite via the standard library, `google-genai` for Gemini.
  Dependencies and venv with `uv` (`backend/pyproject.toml`).
- Entry point: `backend/app/main.py` (`app`); the lifespan creates tables, starts the
  scheduler and loads jobs from the stored profile.
- Run: `make dev` (API on port 8000, one worker: architecture.md "Constraints").

## Structure
- Routes: `app/api/`, one module per resource in api.md. Thin.
- Business logic: `app/agent/`, `app/discovery/`, `app/signals/`, `app/reports/`,
  `app/watcher/`. Signals are pure functions over `Candidate` and `Round` data.
- Data access: `app/store/` only; nothing else writes SQL.
- External services: `app/cala/`, `app/context_dev/`, `app/llm/`, one client each.
- Config: `app/config.py`, a Pydantic settings object read from the environment.
- Shared types: `app/models.py` (api.md).

## Modes (environment)
- `CALA_MODE=live|replay`: replay answers only from the cache and fails clearly on a miss.
- `LLM_MODE=gemini|fake`: fake returns scripted, deterministic answers (tests, offline).
- `DEMO_MODE=1`: enables `/api/demo/simulate-event`.

## Rules
- Handlers stay thin: parse and validate input, call a service, map the result.
- Validate all external input at the boundary. Trust nothing from the client.
- Errors follow the shape in api.md. Never leak stack traces or secrets in responses.
- Config only from environment variables; add every new one to `.env.example`.
- External calls (LLMs, third-party APIs) go through one wrapper per service, with timeout,
  so tests can mock them.
- Gemini output that changes state (profile edits, alerts) is requested as structured output
  or function calls and validated with Pydantic before it is applied.
- Log events with context, never secrets or full personal data.
- Schema/data changes: tables are created at startup (`CREATE TABLE IF NOT EXISTS`); no
  migrations in the MVP. Changing a table means deleting `data/grabbit.db` and re-running
  `make warm`; say so in the PR.
