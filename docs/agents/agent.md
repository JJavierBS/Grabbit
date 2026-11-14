# Agent behaviour

How the Gemini agent personalizes itself, which questions it asks, how signals are computed
and how trust is shown. Read before building the agent, reports, signals or trust badges.
Product flow: flow.md. Types: api.md. Code: `backend/app/signals/`. Keep this file under 100 lines.

## Self-personalization (the originality)
Gemini personalizes the report itself, through the conversation. No settings screen.
- The profile has structured fields (filters, reference investors, style, cadence,
  threshold) and `instructions`: free text that Gemini writes for itself, describing how
  this investor wants reports ("lead with co-investors, skip B2C, two lines per startup").
- Every chat turn, Gemini gets the fixed system prompt, the current profile with its
  `instructions`, the latest report and the user's message. It may call two tools:
  - `update_profile(patch, reason)`: edits structured fields (validated with Pydantic).
  - `rewrite_instructions(text, reason)`: replaces its own `instructions`.
- It also learns from reactions it was not told to act on: "too long", a source opened, a
  startup dismissed. At the end of each turn it decides whether to rewrite `instructions`.
- Each change creates a `ProfileChange` (before, after, reason, `by: agent`) and a new
  profile version. The reply says what changed in one line ("From now on: co-investors
  first.") and the report is regenerated at once, so the change is visible. Undo reverts
  one version.
- Selection constraints use structured fields: `filters.fundraising`, `raised_within_months`,
  `required_backers`; `style.max_candidates` limits cards and prose together. A required
  signal/backer needs positive evidence. Trust alone changes ranking, not eligibility.
- The fixed system prompt holds what self-edits can never change: never recommend what to
  buy, show every fact with its trust badge, never invent a value, absent is "not
  published", Cala facts and web signals stay apart. Instructions that conflict are
  ignored and the agent says so.
- Demo moment: a correction in chat, the report changing in front of the judge, and
  `/api/profile/history` showing what the agent rewrote about itself.

## Trust scale
From Cala `source_rank` (cala.md). A fact with several sources shows the strongest.
| `TrustLevel` | Badge | Source |
| --- | --- | --- |
| `filing` | Official filing | Registries, regulators, SEC, Companies House, GLEIF |
| `primary` | Company or investor | The company, its investors, lenders or grant bodies |
| `press` | Press | Independent publications |
| `aggregator` | Database | Funding databases, data providers |
| `cala_news` | Cala news | Cala's knowledge query summarised the item; no per-item source |
| `web_unverified` | Web, unverified | Context.dev soft signals; never mixed with Cala facts |
| `not_published` | Not published | Field absent in Cala; never shown as 0 |
Dates show only their precision: a `year` date reads "2019", not "2019-01-01".

## Question bank (onboarding and thesis flow)
Each question is backed by data from the current candidate set; ask 2-3, never all of them.
Apply the updated profile before counting or asking. Code builds every question with its numbers and options (`app/agent/onboarding.py`); Gemini
(minimal thinking, alongside the report build) picks the ones that fit the investor's first
message and words them and their options in its language. A worded question whose numbers or
option count differ keeps the bank's wording; on failure the 3 that split the set best are
asked (#165). Numbers in the question come from Cala, not from the model.

| Question | Cala field |
| --- | --- |
| "Of the N startups that match, X are pre-seed or seed and Y Series A or later. Which stage?" | `funding_stage` |
| "Rounds here range from A to B. What ticket do you write?" | `FundingRound.transaction_value` |
| "Which investors do you trust? K attendees are backed by them." | round participants, `is_lead` |
| "Most matches are in industries X and Y. Keep both?" | `OPERATES_IN_INDUSTRY` |
| "Teams range from a to b people. Prefer small teams?" | `employee_count_range`, `employee_count` series |
| "Only startups that grew headcount in the last year?" | `employee_count` series |
| "Startups that raised in the last 12 months, or ones that may raise soon?" | `FundingRound.event_date` |
| "Headquarters: anywhere, or only some countries?" | `HAS_HEADQUARTERS_IN` |

## Signals (v1, pure functions, tuned in code with tests)
- `co_invest`: a reference investor (deduplicated by entity id) took part in one of the
  startup's rounds. Value: their names, leads first, then most recent (`Signal.value` holds
  scalars only); the explanation says who led or joined which round.
- `lead_follow_on`: for the lead of the startup's last round, the share of the lead's other
  portfolio companies where it also joined a later round. Needs 3+ companies, else null.
- `likely_to_raise`: up to three checks, each only if the data exists:
  1. 12 to 30 months since the last `ISSUER` round (`event_date`);
  2. headcount grew 20% or more over the last 12 months (`employee_count` series; the
     latest point must be under 6 months old, else no data);
  3. the last lead's `lead_follow_on` is 0.3 or more.
  True if at least two checks pass; null if fewer than two checks have data. The
  explanation lists each check and its facts. It is a hint, never a recommendation.

## Cadence and alerts
- With an event: a prep report when onboarding ends, a daily digest during the event week,
  a weekly follow-up after it, until the angel says they found a round. Without an event:
  weekly. The watcher runs every 15 minutes in all cases.
- Alert kinds and their Cala source: api.md `Alert`, flow.md section 4. Importance: rules
  first (lead is a reference investor, executive left), then a Gemini score with a one-line
  reason; alert only above the profile's threshold.
