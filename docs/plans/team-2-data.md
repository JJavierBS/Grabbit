# Team 2: Data (Cala, signals, watcher)

Mission: everything Grabbit knows comes from Cala's graph through your code, with its
source and trust level, fast enough for a live demo. Then you make it proactive.

Read first: `docs/agents/cala.md` (all of it), `agent.md` "Signals" and "Trust scale",
`api.md` types, `flow.md` sections 4-5. Cala field guide: `docs/reference/cala-field-guide.md`.

## Owned paths
`backend/app/cala/`, `discovery/`, `signals/`, `watcher/`, `scheduler.py`,
`store/cala_cache.py`, `store/snapshots.py`, `backend/tests/fixtures/cala/`,
`backend/scripts/warm.py`.

## 0. Start now (no dependency on the skeleton)
1. With your `CALA_API_KEY`, record real responses (plain httpx script, not committed if
   it holds the key) for:
   - Slush 2026 `Event` `bc844d56-6ab4-452b-96bf-2661e86e592b`, incoming
     `PARTICIPATES_IN_EVENT`, `limit: 100`, first two pages;
   - five startups among the attendees: introspection, then retrieval with properties,
     `PARTICIPATES_IN_FUNDING_ROUND`, founders and executives, `employee_count` series;
   - two `FundingRound`s with their participants; two lead investors with their rounds.
2. Trim them (keep real shapes, drop bulk) into `backend/tests/fixtures/cala/`. Never
   commit the key. These fixtures unblock your tests and Team 3's.
3. Count attendees and how many look like startups; post the numbers (pitch, D2).

## 1. #22 Cala client (merge by 10:00)
- `cala/client.py`: async httpx, base URL, `X-API-KEY`, timeout, concurrency semaphore,
  retry with exponential backoff on 429 and 5xx, a call budget logged per run.
- Cache (`store/cala_cache.py`): key = method + path + body hash; `CALA_MODE=replay`
  serves only cache and raises a clear error on a miss.
- `cala/normalize.py`: response -> `Fact`. Handle both `document` shapes, map
  `source_rank` -> `TrustLevel`, strongest source wins, keep `date_precision`, absent ->
  `not_published`. This is what the trust badges show: test it hard.
- Tests on your fixtures with respx; no network.

## 2. #23 Slush discovery pipeline (merge by 13:00)
- `discovery/event.py`: page attendees of an `Event`; `discovery/filter.py`: drop funds
  and corporates by founding date, `funding_stage`, headcount (thresholds in config).
- `discovery/candidates.py`: build `Candidate`s; rounds from `FundingRound` with
  `role: ISSUER`; investors from participants with `is_lead`; dedupe investors by id,
  `website`, normalised name (cala.md "Data quirks").
- Public function for Team 3: `get_candidates(profile) -> list[Candidate]`, filtered by
  the profile's filters. Agree its signature with Team 3 at M0 and keep it stable.
- `backend/scripts/warm.py` behind `make warm`: fills the cache for the event and the demo
  path, prints counts.
- With Teams 3 and 4, fix the demo thesis and reference investors (open-questions D2):
  5-10 startups with recent rounds and a known lead, at least one with a dated event for
  the alert (R3).

## 3. #24 Signals (in parallel with #23, merge by 13:00)
Pure functions in `signals/`, exactly as agent.md "Signals (v1)": `co_invest`,
`lead_follow_on`, `likely_to_raise`. Inject the clock. `value=null` on missing data, with
an explanation that says what is missing. One test per check, per missing-data case.

## 4. #28 Watcher and scheduler (start at M2, merge by 18:00)
- `store/snapshots.py`: last state per shortlisted entity.
- `watcher/diff.py`: alert kinds in api.md from Cala edges (new round and its lead,
  executive joins or leaves via `valid_since`/`valid_until`, headcount jump, acquisition,
  status or domain change).
- `watcher/importance.py`: rules first (lead is a reference investor, executive left),
  then Team 3's Gemini scorer (`llm.score_alert`), threshold from the profile.
- `scheduler.py`: APScheduler jobs from the cadence in agent.md; watcher every 15 min; no
  overlapping runs; jobs reloaded when the profile changes.
- Publish alerts with `events.publish("alert", alert)` (Team 1's broadcaster).
- `POST /api/demo/simulate-event`: loads a fixture from `backend/app/fixtures/demo_events/`
  (never from the Cala cache), runs it through the same diff, importance and delivery
  path, `simulated=true`.
- Tests: one per alert kind, threshold, dedupe, simulate-event end to end with FakeLLM.

## Interfaces you provide
`get_candidates(profile)`, `compute_signals(candidate, profile)`, `watcher.run_once()`,
the normalised `Fact`. Changing a signature: tell Team 3 first.
