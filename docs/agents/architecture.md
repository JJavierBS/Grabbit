# Architecture

Keep this file under 80 lines. Update it in the PR that adds or moves a module.

## Overview
One FastAPI process serves the API and the built React app, and runs the scheduler in the
same process. The browser talks to `/api/*` and listens to `/api/events` (Server-Sent
Events) for alerts. The backend walks Cala's graph through one cached client, scores
signals with pure functions, and asks Gemini to chat, to rewrite its own report
instructions (agent.md "Self-personalization") and to write reports. No login: each browser
is an anonymous workspace (`app/workspace.py`), so demo visitors never share state.

## Components
Owners are assigned on the issues; the board is the source of truth.
| Component | Path | Purpose |
| --- | --- | --- |
| API routes | `backend/app/api/` | Thin handlers for the endpoints in api.md |
| Shared models | `backend/app/models.py` | Pydantic types in api.md; the frontend types are generated from them |
| Event bus | `backend/app/events.py` | `publish(kind, payload)` fans out to every `/api/events` SSE subscriber |
| API fixtures | `backend/app/fixtures/` | Mock data for the endpoints and frontend tests; `demo_events/` for the simulated alert |
| Cala client | `backend/app/cala/` | Only door to Cala: queue, timeout, retry on 429, cache, normalise to `Fact` |
| Context.dev client | `backend/app/context_dev/` | Soft signals only, labelled "web, unverified" |
| LLM client | `backend/app/llm/` | Only door to Gemini; `FakeLLM` for tests and offline demo |
| Event pipeline | `backend/app/discovery/` | Event attendees -> local startup filter -> candidates with rounds |
| Signals | `backend/app/signals/` | Pure functions: co-invest, lead follow-on, likely to raise soon |
| Agent | `backend/app/agent/` | Chat, question bank, tools that edit the profile and its own instructions |
| Reports | `backend/app/reports/` | Builds `Report` from candidates, signals, profile and instructions |
| Watcher | `backend/app/watcher/` | Snapshots, diff, importance check, `Alert` |
| Scheduler | `backend/app/scheduler.py` | APScheduler jobs: digest and watcher per profile |
| Runtime glue | `backend/app/runtime.py` | Cala session on the shared cache; the jobs the lifespan schedules (watcher over the latest report, digest) |
| Store | `backend/app/store/` | SQLite access: `db.py` (connection, `register_table`), one `<domain>.py` per team |
| Web app | `frontend/src/` | Chat, report with trust badges, alerts, desktop notifications |

## Data
- Storage: one SQLite file (`DATABASE_PATH`, default `data/grabbit.db`, gitignored). Tables
  are created at startup; no migrations in the MVP. `make warm` fills the Cala cache.
- Workspaces: the `X-Workspace` header (or `?workspace=` on SSE) picks the visitor; missing
  means `default`. Profile, chat, reports, snapshots and alerts carry a `workspace` column and
  stores filter by `workspace.current()`; events reach only that workspace's streams. The
  Cala and Context.dev caches and investor names stay shared. A table registered with
  `db.drop_if_missing` is dropped at startup when an older file lacks the column.
- Main entities: `Profile` (filters, reference investors, style, cadence, threshold,
  `instructions` written by Gemini, `version`), `ProfileVersion` (diff, reason, author),
  `Snapshot` (entity id, hash, payload, taken_at), `Report`, `Alert`, `CalaCache` (key =
  method + path + body hash, response, fetched_at). Shapes: api.md.

## External services
| Service | Used for | Env vars |
| --- | --- | --- |
| Cala API (`https://api.cala.ai`) | Discovery from `Event`, companies, rounds, investors, people | `CALA_API_KEY`, `CALA_MODE` |
| Context.dev (`https://api.context.dev/v1`) | Soft signals only (decisions.md) | `CONTEXT_DEV_API_KEY` |
| Gemini API (Google DeepMind), SDK `google-genai` | Chat, self-personalization, report writing, importance score | `GEMINI_API_KEY`, `GEMINI_MODEL`, `LLM_MODE` |
| AWS Lightsail container service | Deployed demo link over HTTPS (desktop notifications need it) | set in the service, never in git |

## Directory layout
- `backend/`: FastAPI app (`app/`), tests (`tests/`), `pyproject.toml` managed by `uv`.
- `frontend/`: Vite + React + TypeScript app (`src/`), tests next to components.
- `data/`: local SQLite and cache, gitignored.
- `docs/`: agent docs (`agents/`), raw references (`reference/`), research (`research/`).
- `scripts/`: setup, hooks, board, docs mirror.
- `Dockerfile`: multi-stage, builds the frontend and serves it from FastAPI.

## Constraints
- Demo must run from a clean clone with `make setup && make dev`.
- Demo runs from our own laptop on crowded venue wifi: the core flow must work locally, with
  cached or recorded responses as fallback for slow external APIs (`CALA_MODE=replay`).
- A deployed demo link is required in the submission.
- Cala must be core to the product, not an add-on (25% of the partner score).
- All Cala calls go through one wrapper with timeout and a response cache.
- One uvicorn worker only: the scheduler lives in the process, more workers would duplicate
  jobs. The watcher and digest loop over every workspace with a report; only the default
  workspace sets the shared digest cadence.
