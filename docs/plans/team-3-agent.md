# Team 3: Agent (Gemini, self-personalization, reports)

Mission: build the originality. The angel corrects the report in plain words, Gemini
rewrites its own instructions, and the report changes on screen. Then write every report.

Read first: `docs/agents/agent.md` (all of it), `flow.md` sections 1-3, `api.md` types,
`backend.md` "Rules" (validated structured output).

## Owned paths
`backend/app/llm/`, `agent/`, `reports/`, `context_dev/`, `store/profile.py`,
`store/chat.py`, `store/reports.py`, `backend/app/fixtures/llm/` (FakeLLM scripts).

## 0. Start now (no dependency on the skeleton)
1. Gemini spike in a scratch script: with `GEMINI_API_KEY`, pick `GEMINI_MODEL` (fast
   model for chat, check ai.google.dev for current ids), confirm function calling and
   structured output with `google-genai`. Note latency per call; post the model id.
2. Draft the fixed system prompt: the rules self-edits can never change (agent.md
   "Self-personalization"): never recommend what to buy, never invent a value, every fact
   with its trust badge, absent is "not published", Cala facts and web signals apart.
3. Draft the tool schemas `update_profile(patch, reason)` and
   `rewrite_instructions(text, reason)` and ten example user turns with the expected tool
   call; they become FakeLLM scripts and tests.

## 1. #25 Self-personalizing agent (core by 10:00, merge by 13:00)
- `llm/client.py`: one door to Gemini, timeout, retries, function calling, structured
  output parsed into Pydantic. `llm/fake.py`: `FakeLLM` replays scripts from
  `fixtures/llm/` by matching the user text; deterministic.
- `store/profile.py`: current `Profile`, `ProfileVersion` rows, `ProfileChange` history;
  `undo()` restores the previous version.
- `agent/chat.py`: each turn sends system prompt + profile + `instructions` + latest
  report summary + message; applies validated tool calls; ends with a one-line "From now
  on: ..." when something changed. Refuses and says so when an instruction breaks a fixed
  rule.
- `agent/learn.py`: after each turn, decides whether reactions ("too long", a dismissed
  startup) justify rewriting `instructions`.
- `agent/onboarding.py`: picks the 2-3 questions from the agent.md bank that best split
  the current candidates; numbers in questions come from data (Team 2's `get_candidates`;
  use the skeleton fixtures until #23 lands).
- Endpoints made real: `POST/GET /api/chat`, `GET /api/profile`, `/history`, `/undo`.
  Publish `profile` on the events bus after a change.
- Tests with FakeLLM: a correction edits the profile, a rewrite stores a version with its
  reason, a forbidden instruction is refused, undo restores, onboarding questions carry
  real numbers.

## 2. #26 Report builder (start at M1, merge by 14:00 for M2)
- `reports/rank.py`: order candidates by the profile (default: co-invest with a
  reference investor as lead first, then `likely_to_raise`).
- `reports/write.py`: Gemini writes the summary and one short paragraph per startup,
  following the profile `style` and `instructions`. Numbers are never written by the
  model: pass facts with ids, let the model reference them, render values from `Fact`s
  server-side. Reject and retry once if the text contains a number that is not a fact.
- Kinds: `prep` (after onboarding), `digest` (scheduled, only what changed), `memo` (on
  request in chat).
- A profile change from #25 triggers a rebuild and `events.publish("report", {id})`, so
  Team 4 can highlight what changed.
- `POST /api/reports/run`, `GET /api/reports/latest` real.
- Also provide `llm.score_alert(alert, profile) -> (score, reason)` for Team 2's watcher.
- Tests with FakeLLM: new `instructions` or filters change the report; no invented
  numbers; `not_published` survives into the report.

## 3. #34 Context.dev soft signals (prio:nice, only after M3)
Client with timeout and cache; allow-list from onboarding; `Fact`s with
`trust=web_unverified`; their own block in the report. Read `docs/agents/context-dev.md`.

## Integration
Merge order, files touched outside our paths and what other teams adapt:
`docs/plans/team-3-integration.md`.

## Demo responsibility
The 20-second moment in the video: "shorter, co-investors first" -> the report rewrites
itself -> history shows what the agent learned. Make it reliable: script it in FakeLLM
too, so it works offline.
