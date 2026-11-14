# API contract

Contract first: change the contract, then the backend and frontend. This lets both sides
work in parallel against mocks.

- Source of truth: Pydantic models in `backend/app/models.py`. FastAPI publishes them at
  `/api/openapi.json`; `npm run gen:api` (openapi-typescript) writes
  `frontend/src/api/schema.ts`, committed. Never hand-write API types in the frontend.
- Mocks: every endpoint exists from the skeleton issue on, first returning fixture data
  (`backend/app/fixtures/`, status "mock" below). The frontend always talks to the real
  backend; offline it runs with `CALA_MODE=replay` and `LLM_MODE=fake`.
- Base URL: local, Vite on `http://localhost:5173` proxies `/api` to FastAPI on `:8000`.
  Deployed, same origin.

## Rules
- A PR changing the contract updates contract, mocks and both sides' types together, or
  opens issues for the side it does not touch.
- Breaking changes use `!` in the PR title and are announced in the team chat.
- Error shape for every endpoint: `{ "error": { "code": "snake_case", "message": "..." } }`
  with a matching HTTP status.
- Names: snake_case in JSON. Dates ISO 8601. Money as number plus `unit` (currency code).
- Single user in the MVP: no auth, one profile.

## Shared types
`?` marks nullable. Enum values are lowercase strings.
- `TrustLevel`: `filing | primary | press | aggregator | web_unverified | not_published`
  (meaning and badges: agent.md "Trust scale").
- `Source`: `name, url?, date?, date_precision? (day|month|year), rank: TrustLevel`.
- `Fact`: `value? (string|number|bool|list), unit?, trust: TrustLevel, sources: Source[]`.
  `trust` is the strongest source's rank. Absent in Cala: `value=null`,
  `trust=not_published`, `sources=[]`. Never turn absent into 0.
- `Investor`: `entity_id, name, is_lead, role (investor|lender)`.
- `Round`: `entity_id, label?, name, amount: Fact, date: Fact, investors: Investor[]`.
- `Signal`: `kind (co_invest|lead_follow_on|likely_to_raise), label, value?, explanation,
  facts: Fact[]`. `value=null` means not enough data, shown as such.
- `Candidate`: `entity_id, name, website?, description?, founding_date: Fact,
  funding_stage: Fact, headcount: Fact, total_funding: Fact, hq: Fact, industries: string[],
  rounds: Round[], signals: Signal[]`.
- `Profile`: `version, event_id?, thesis, filters {stages[], sectors_in[], sectors_out[],
  countries[], headcount_max?, ticket?: Fact}, reference_investors [{entity_id, name}],
  style {length (short|medium|long), detail (plain|technical), language, sections[]},
  cadence (event|daily|weekly), alert_threshold (low|medium|high), sources[] (publisher
  domains the angel trusts, the Context.dev allow-list; up to 3 are queried), instructions,
  updated_at`.
- `ProfileChange`: `version, field, before, after, reason, by (user|agent)`.
- `ChatMessage`: `id, role (user|agent), text, created_at, profile_changes: ProfileChange[],
  report_id?`.
- `Report`: `id, kind (prep|digest|memo), created_at, profile_version, summary,
  sections [{title, body_md, candidate_ids[]}], candidates: Candidate[]`.
- `Alert`: `id, created_at, entity_id, entity_name, kind (new_round|executive_change|
  headcount_jump|acquisition|status_change|web_news), title, why_it_matters,
  importance (0-1), facts: Fact[], simulated: bool`. `simulated=true` is shown on screen.
- `Health`: `status ("ok"), cala_mode (live|replay), llm_mode (gemini|fake), demo_mode: bool`.
- Request bodies: `ChatRequest {text}` (1-4000 chars), `ReportRunRequest {kind}`,
  `SimulateEventRequest {fixture}` (a file name in `backend/app/fixtures/demo_events/`).
- `ErrorResponse`: `{error: {code, message}}`. Codes so far: `not_found`,
  `validation_error`, `internal_error`, `demo_mode_disabled`, `fixture_not_found`.

## Endpoints
| Method | Path | Purpose | Status |
| --- | --- | --- | --- |
| GET | `/api/health` | Liveness and modes (`cala_mode`, `llm_mode`, `demo_mode`) | mock |
| GET | `/api/profile` | Current `Profile` | mock |
| GET | `/api/profile/history` | `ProfileChange[]`, newest first | mock |
| POST | `/api/profile/undo` | Revert the last change, returns `Profile` | mock |
| GET | `/api/chat` | `ChatMessage[]` of the conversation | mock |
| POST | `/api/chat` | `{text}` -> agent `ChatMessage` (may change the profile and regenerate the report) | mock |
| GET | `/api/reports/latest` | Latest `Report` | mock |
| GET | `/api/reports` | Past `Report[]`, newest first, at most 20 (#54) | mock |
| POST | `/api/reports/run` | `{kind}` -> new `Report` ("run now" for the demo) | mock |
| GET | `/api/alerts` | `Alert[]`, newest first | mock |
| GET | `/api/events` | SSE stream: `alert` (Alert), `report` ({id}), `profile` (Profile) | mock |
| POST | `/api/demo/simulate-event` | `{fixture}` -> `Alert` through the real watcher path; only with `DEMO_MODE=1` | mock |
