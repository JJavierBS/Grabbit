# Team 1: Platform

Mission: give the other three teams a running, tested shell within 90 minutes, then keep
the integration healthy, deploy it and own the demo. You are the critical path until M0.

Read first: `docs/agents/architecture.md`, `api.md`, `backend.md`, `frontend.md`,
`testing.md`. Index and milestones: `docs/plans/README.md`.

## Owned paths
`Makefile`, `Dockerfile`, `.env.example`, `.gitignore`, `backend/pyproject.toml`,
`backend/app/main.py`, `config.py`, `models.py`, `events.py`, `api/`, `store/db.py`,
`fixtures/`, `frontend/` scaffold (`package.json`, `vite.config.ts`, `src/main.tsx`,
`src/api/`), `README.md`.

## 1. #21 Project skeleton (start now, merge by 06:00)
Keep it thin: the goal is unblocking, not features.
1. Backend: `uv init` in `backend/`, Python 3.12; deps fastapi, uvicorn, pydantic,
   pydantic-settings, httpx, apscheduler, google-genai, sse-starlette; dev deps pytest,
   pytest-asyncio, respx, ruff.
2. `app/models.py`: every type in api.md "Shared types", field for field. Enums as
   `Literal`s. This file is the contract; get it right first and push it early.
3. `app/config.py`: settings for every variable in `.env.example`.
4. `app/events.py`: in-process broadcaster, `publish(kind, payload)` and an async
   subscriber used by `/api/events`. Teams 2 and 3 publish through it.
5. `app/store/db.py`: SQLite connection from `DATABASE_PATH`, a `register_table(sql)`
   hook and `init_db()` called in the lifespan. Teams add their own `store/<domain>.py`.
6. `app/fixtures/`: realistic JSON for each endpoint. At least three candidates with full
   `Fact`s covering every `TrustLevel` (one `not_published`, one year-precision date),
   rounds with a lead, all three signals (one with `value=null`), a report, two alerts
   (one `simulated`), a profile with history. Teams 3 and 4 build on these for hours.
7. `app/api/`: one router per resource, every endpoint in api.md returning fixtures, the
   error shape from api.md, `/api/health` with modes. Lifespan: `init_db()`, scheduler
   started empty (Team 2 adds jobs).
8. Frontend: Vite `react-ts`, TanStack Query, openapi-typescript. `npm run gen:api` writes
   `src/api/schema.ts` from `http://localhost:8000/api/openapi.json`; `src/api/client.ts`
   is the single client. Vite proxy `/api` -> `:8000`. A placeholder screen showing
   `/api/health`. Team 4 replaces the UI.
9. Tooling: ruff (lint + format), Biome for the frontend (lint + format), Vitest + Testing
   Library (jsdom). Makefile: `setup` (uv sync, npm ci, `scripts/setup.sh`), `dev` (both
   servers, one command), `test` (pytest -q + vitest run, quiet), `lint`, `fmt` (changed
   files only, `git diff --name-only origin/main...`), `warm` (calls Team 2's warm script,
   placeholder until #23).
10. `Dockerfile`: stage 1 builds the frontend, stage 2 runs uvicorn with one worker and
    serves `frontend/dist` as static files at `/`.
11. Tests: `/api/health`, one fixture endpoint per router, frontend renders.
12. Merge, then post in the team chat: "M0 done, pull main".

## 2. Integration duty (from M0 to freeze)
- Review contract PRs from other teams within 15 minutes.
- After each merge to main, run `make dev` and click through the demo path; open a bug
  issue for what breaks and tag the owning team.
- Create the submission issues under the "Final submission" milestone if they do not
  exist: video, deck PDF, final form, rehearsal (workflow.md).

## 3. #29 Deploy to AWS Lightsail (start after M0, first deploy by M2)
1. AWS Lightsail container service (nano or micro), one container, port 8000, public
   HTTPS endpoint. Secrets as service environment variables, never in git.
2. Push the image built from the `Dockerfile`; document the commands in README "Deploy".
3. Ship the warmed SQLite cache in the image or at start, so the deployed link works with
   `CALA_MODE=replay` if Cala is slow.
4. Check from a clean browser: page loads over HTTPS, desktop notification permission
   prompt appears, `/api/events` stays open.
5. Redeploy after M3 and M4.

## 4. #30 README, punchline, pitch number (after M2, finish after freeze)
pitch.md is the source. Count of Slush attendees and startups comes from `make warm`
(Team 2). Mention the investor interviews, pseudonymised.

## 5. Demo owner (M4)
Run the demo script in challenge.md end to end twice, timed, on the projector resolution
(1920x1080). Keep a list of what failed and route it to the owning team.
