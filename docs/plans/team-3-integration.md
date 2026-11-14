# Team 3 integration notes

What changes when the Team 3 branches land, in which order, and what other teams must adapt.
Branches: `25-self-personalizing-agent` (PR #39), `26-report-builder` (PR #47),
`34-context-dev-signals` (PR #49). Each is stacked on the previous one; #39 is stacked on #21.

## 1. Merge order
1. #21 skeleton (Team 1) into `main`.
2. #39 (#25 agent), then #47 (#26 reports), then #49 (#34 Context.dev).

PRs are squash-merged, so after each merge the next branch still carries the old commits.
Before merging the next PR, the owner (or whoever merges) runs on that branch:
```
git fetch origin && git merge origin/main
```
Conflicts there are files the branch already contains in full: keep the branch version
(`git checkout --ours <file>`), except `docs/agents/decisions.md`, where both sides only append
lines: keep every line once. Then `make test lint` and push. If GitHub did not retarget the PR
after its base branch was deleted, set the base to `main` (`gh pr edit <n> --base main`).

## 2. Files outside Team 3's paths that these PRs change
| File | PR | Change | Why |
| --- | --- | --- | --- |
| `backend/app/api/chat.py`, `profile.py` | #39 | Real handlers instead of fixtures | #25 makes these endpoints real (api.md) |
| `backend/app/api/reports.py` | #47 | Real handlers; `GET /latest` is 404 `no_report` before the first run | #26 |
| `backend/app/services.py` (new) | #39, #47 | Hooks the agent calls: report rebuild, latest summary | keeps `agent/` free of report imports |
| `backend/app/config.py` | #39 | `gemini_timeout_s` (`GEMINI_TIMEOUT_S`) | Gemini client timeout |
| `backend/tests/conftest.py` | #39, #47 | Autouse `agent_db` (tables on the test database, fresh FakeLLM and Context.dev client), `now` and `published` fixtures; `client` waits for background report rebuilds before closing | tests for the agent and reports |
| `backend/tests/test_api_mocks.py` | #39, #47 | Profile, chat and reports checks assert real behaviour, not fixture data (fresh profile is version 1, undo is 409, no report before a run) | those endpoints are no longer mocks |
| `backend/app/models.py`, `api.md`, `frontend/src/api/schema.ts`, `fixtures/profile.json` | #49 | Additive contract change: `Profile.sources: string[]` | Context.dev allow-list (flow.md onboarding step 4) |
| `.env.example` | #39 | `GEMINI_MODEL=gemini-3.5-flash`, `GEMINI_TIMEOUT_S` | model picked by the spike (decisions.md) |

## 3. What other teams must adapt
**Team 1 (platform)**
- Background report rebuilds run as asyncio tasks in the API process
  (`app/reports/service.py`). On shutdown they are cancelled; to let them finish, await
  `app.reports.service.wait_idle()` in the lifespan before the scheduler shuts down (optional).
- New SQLite tables: `profile_versions`, `profile_changes`, `chat_messages`, `reports`,
  `context_dev_cache`. Deployed or local databases created before these PRs need no action
  (`CREATE TABLE IF NOT EXISTS`); a later change to one of them means deleting `data/grabbit.db`.
- Deploy env (#29): `GEMINI_API_KEY`, `GEMINI_MODEL`, optional `CONTEXT_DEV_API_KEY`.

**Team 2 (data)**
- Candidates come from `app/agent/sources.py::candidates_for(profile)`, which reads the
  fictional fixture `app/fixtures/candidates.json` (`TODO(#23)`). Replace its body with the
  Slush discovery pipeline; nothing else in the agent or reports needs to change.
- Reference investors named in chat are stored with `entity_id = "unresolved:<name>"`. Resolve
  them to Cala entities (flow.md onboarding step 2) and rewrite the id.
- Ranking reads `Candidate.signals` (`likely_to_raise` value `true`) when #24 fills them; until
  then co-invest is computed from round participants in `reports/rank.py`.
- Watcher (#28): score alerts with `app.llm.scoring.score_alert(llm, alert, profile)` ->
  `(score, reason)`; it returns `(0.5, "Not scored...")` when Gemini is down. Run the digest with
  `app.reports.service.run("digest")`; it reports only new startups or new rounds since the
  previous report and says "Nothing new since the last report." otherwise.

**Team 4 (frontend)**
- `POST /api/chat` answers before the report is rebuilt (about 13 s with Gemini). The reply's
  `report_id` is the id the new report will have: wait for the SSE `report` event with that id,
  then fetch `GET /api/reports/latest`. A rebuild superseded by a newer correction is dropped,
  so only the newest id ever arrives.
- `GET /api/reports/latest` is 404 `no_report` until the first `POST /api/reports/run`: show an
  empty state or run `prep` after onboarding.
- `POST /api/profile/undo` with nothing to undo is 409 `nothing_to_undo`.
- Report sections: "Co-invest with investors you trust", "Likely to raise soon", "Other
  matches" (digest: "What changed"), and last "Web signals (unverified)", which must keep its
  own look (never mixed with Cala facts). Badges are already rendered in `body_md`.
- `Profile.sources` (publisher domains) can be shown in the profile view.

## 4. Modes and keys
- Offline (tests, demo on bad wifi): `LLM_MODE=fake` replays `app/fixtures/llm/*.json`;
  `CALA_MODE=replay` also makes Context.dev read only its cache.
- Gemini check: `cd backend && uv run python scripts/gemini_spike.py` (needs `.env`).
- Measured with `gemini-3.5-flash`: chat turn about 9 s, report writing about 13 s.
