# How Grabbit works

A visual tour of the system for readers who have not followed the issues: the user flow,
the architecture, how a chat turn walks Cala's graph, how the agent rewrites itself, how
startups are ranked, and how alerts reach the investor. Each section links to the code and
to the longer documents behind it.

> [!NOTE]
> The diagrams are Mermaid and render on GitHub. The numbers come from
> [algorithm.md](algorithm.md), which explains how each one was measured.

## Contents

- [The user's journey](#the-users-journey)
- [Architecture](#architecture)
- [A chat turn, step by step](#a-chat-turn-step-by-step)
- [Discovery: two walks over Cala's graph](#discovery-two-walks-over-calas-graph)
- [Ranking: the proximity score](#ranking-the-proximity-score)
- [Trust: from `source_rank` to a badge](#trust-from-source_rank-to-a-badge)
- [Self-personalization: the agent rewrites itself](#self-personalization-the-agent-rewrites-itself)
- [Proactivity: watcher, digest and alerts](#proactivity-watcher-digest-and-alerts)
- [Guardrails](#guardrails)
- [Data model](#data-model)
- [Where things live](#where-things-live)

## The user's journey

One flow for one persona: a business angel preparing Slush 2026
([flow.md](agents/flow.md)).

```mermaid
journey
  title A business angel preparing Slush 2026 with Grabbit
  section Before Grabbit
    40 tabs for eight startups: 1: Angel
    Arrives tired at the decision: 1: Angel
  section Onboarding
    Types a vague thesis: 4: Angel
    Answers questions backed by numbers: 4: Angel, Grabbit
    Names the investors they trust: 5: Angel
  section Report
    Reads a ranked shortlist with sources: 5: Angel, Grabbit
    Corrects it in plain words: 5: Angel, Grabbit
  section After
    Leaves, Grabbit watches the shortlist: 5: Grabbit
    Gets an alert when a startup moves: 5: Angel, Grabbit
```

| Screen | |
| --- | --- |
| ![Start](images/01-start.png) | **Start vague.** One box, one sentence. Suggestions for a first try. |
| ![Questions](images/02-questions.png) | **It asks before it answers.** Each question carries a number from the candidate set ("7 out of 11 raised funding in the last 12 months"). The violet note says what the agent changed in its own instructions, with an undo. |
| ![Report and alert](images/03-report-alert.png) | **Report, correction, alert.** "Co-invest with investors you trust" leads the report; "Shorter, one line per startup" rewrote it; the staged alert lands, labelled "Simulated event". |

## Architecture

One FastAPI process serves the API and runs the scheduler. The browser talks REST and
listens to a Server-Sent Events stream. Every call to Cala goes through one cached client
([architecture.md](agents/architecture.md)).

```mermaid
flowchart TB
  subgraph Browser["Browser (React + TypeScript, Vite)"]
    UI["Chat, report panel,<br/>trust badges, Why-it-is-here graph"]
    Notif["Toasts and desktop<br/>notifications"]
    Mic["Talk: live transcription"]
  end

  subgraph Edge["Vercel"]
    Static["Static frontend<br/>www.grabbit.cloud"]
    Proxy["/api/* rewrite"]
  end

  subgraph API["FastAPI process (Aiven Runtime, Docker)"]
    Routes["API routes<br/>/api/chat, /api/reports, /api/events ..."]
    Agent["Agent<br/>chat, tools, learn, rules"]
    Disc["Discovery<br/>event walk, reverse walk, proximity"]
    Reports["Reports<br/>rank, facts, write"]
    Watcher["Watcher<br/>snapshot, diff, importance"]
    Sched["APScheduler<br/>watcher 15 min, digest, news 6 h"]
    Bus["Event bus → SSE"]
    CalaC["Cala client<br/>queue, backoff, cache, normalise"]
    LLM["LLM client<br/>Gemini or FakeLLM"]
    Store[("SQLite<br/>profile, chat, reports,<br/>snapshots, Cala cache")]
  end

  Valkey[("Aiven for Valkey<br/>shared Cala cache")]
  Cala[["Cala API<br/>entity graph"]]
  Gemini[["Gemini API"]]
  Ctx[["Context.dev<br/>web, unverified"]]

  UI --> Static
  UI -- "REST" --> Proxy --> Routes
  Bus -- "SSE: progress, trace,<br/>report, alert" --> UI
  Bus --> Notif
  Mic -- "ephemeral token" --> Gemini
  Routes --> Agent --> Disc --> CalaC
  Agent --> Reports --> LLM
  Agent --> LLM
  Sched --> Watcher --> CalaC
  Sched --> Reports
  Watcher --> Bus
  Reports --> Bus
  CalaC <--> Store
  CalaC <--> Valkey
  CalaC --> Cala
  LLM --> Gemini
  Reports -.-> Ctx
```

Design choices worth knowing:

| Choice | Why |
| --- | --- |
| One process, one worker | The scheduler lives in the process; more workers would duplicate jobs |
| No login, one anonymous workspace per browser | Demo visitors never share state; caches stay shared |
| Server-Sent Events, not websockets | One-way push is all alerts and progress need |
| Pydantic models generate the TypeScript client | The frontend cannot drift from the API |
| `CALA_MODE=replay` and `LLM_MODE=fake` | The whole product runs offline, for tests and bad wifi |

## A chat turn, step by step

What happens between "I trust Y Combinator and 500 Global" and the report opening.

```mermaid
sequenceDiagram
  autonumber
  actor Angel
  participant UI as Browser
  participant API as FastAPI
  participant Agent as Agent (Gemini)
  participant Disc as Discovery
  participant Cala as Cala client
  participant Rep as Reports

  Angel->>UI: "I trust Y Combinator and 500 Global"
  UI->>API: POST /api/chat
  API->>Agent: profile + instructions + latest report + message
  Agent->>API: tool call update_profile(reference investors, reason)
  API-->>UI: SSE progress "Walking the Slush attendees in Cala..."
  API->>Disc: candidates for the profile
  Disc->>Cala: event walk (attendees, companies, rounds)
  Disc->>Cala: reverse walk (fund entities → rounds → issuers)
  Cala-->>Disc: cached or live responses, normalised to sourced Facts
  Disc->>Disc: proximity score per candidate
  API->>Rep: build report (deterministic rank)
  Rep->>Agent: write prose with {placeholders} only
  Agent-->>Rep: draft
  Rep->>Rep: reject digits or unknown placeholders, render values from Facts with badges
  API-->>UI: chat reply + "From now on: ..." + SSE report
  UI-->>Angel: report opens, changes highlighted
```

## Discovery: two walks over Cala's graph

Cala returns one node per call and has no "list by criteria". Reading 2,989 attendees costs
about 9,000 serial calls. So Grabbit meets in the middle: it expands the few investors the
angel trusts towards the attendee list and intersects
([algorithm.md](algorithm.md#the-new-algorithm)).

```mermaid
flowchart LR
  subgraph EventWalk["Event walk"]
    Ev["Event: Slush 2026"] --> Att["First 150 attendees"]
    Att --> SU1["Startups<br/>(startup rules)"]
  end

  subgraph ReverseWalk["Reverse walk (from trust)"]
    T["Trusted investor<br/>e.g. Y Combinator"] --> FE["All its fund entities<br/>Company, Organization,<br/>'Y Combinator W24' ..."]
    FE --> Rd["Its funded rounds"]
    Rd --> Iss["Each round's issuer"]
    Rd --> Co["Co-investors<br/>≥ 2 shared rounds"]
    Co --> Rd2["Their rounds<br/>(second ring)"] --> Iss
  end

  AL[("Full attendee list<br/>30 pages, cached")]
  Iss -- "attends Slush?" --> AL
  AL --> SU2["Attending startups"]
  SU1 --> M["Merge and dedupe"]
  SU2 --> M
  M --> F["Profile filters, signals,<br/>hidden links"] --> S["Proximity score"] --> Rank["Ranked shortlist"]
```

The graph it walks, in Cala's own terms:

```mermaid
graph LR
  I(("Investor")) -- "PARTICIPATES_IN_FUNDING_ROUND<br/>role INVESTOR / LENDER / GRANTOR<br/>is_lead" --> R["FundingRound<br/>date, amount, sources"]
  C(("Company")) -- "PARTICIPATES_IN_FUNDING_ROUND<br/>role ISSUER" --> R
  C -- "PARTICIPATES_IN_EVENT<br/>ATTENDEE" --> E["Event: Slush 2026"]
```

What it changed, with Y Combinator and 500 Global as trusted investors:

```mermaid
xychart-beta
  title "Startups found with a trusted investor in their rounds"
  x-axis ["Event walk only", "Ring 1", "Ring 1 + ring 2"]
  y-axis "Startups" 0 --> 30
  bar [5, 27, 27]
```

| KPI | Before | Ring 1 | Ring 1 + ring 2 |
| --- | --- | --- | --- |
| Candidates | 74 | 96 | 108 |
| Startups with a trusted investor in their rounds | 5 | 27 | 27 |
| Candidates with any path to a trusted investor | 5 | 33 | 45 |
| New startups the event walk never saw | 0 | 22 | 34 |

## Ranking: the proximity score

A path joins a startup to a trusted investor. Ring 1: the trusted investor took part in one
of the startup's rounds. Ring 2: one of the startup's investors shared another round with a
trusted investor. Each path's strength is a product of factors; the score is the sum of the
five strongest paths, and those five are the ones shown, so the number is never a black box
([algorithm.md](algorithm.md#4-proximity-score-192)).

```mermaid
flowchart LR
  P["Path"] --> D["Distance<br/>ring 1 = 1.0<br/>ring 2 = 0.3"]
  P --> Ro["Role<br/>lead 1.0<br/>participant 0.6"]
  P --> Re["Recency<br/>halves every 3 years<br/>no date 0.5"]
  P --> So["Source (weakest edge)<br/>filing 1.0, primary 0.9<br/>press 0.75, aggregator 0.6"]
  P --> Se["Selectivity (ring 2)<br/>1 / log2(2 + rounds<br/>of the intermediary)"]
  D & Ro & Re & So & Se --> X(("×")) --> Sum["Score = sum of the<br/>5 strongest paths"]
```

Worked example, trusted investor Y Combinator:

| Startup | Path | Strength |
| --- | --- | --- |
| A | Y Combinator led its 2026 Seed, reported by the company | 1.0 × 1.0 × ~1.0 × 0.9 = **0.90** |
| B | A small fund (6 rounds) joined its round and shared a 2025 round with Y Combinator, both from press | 0.3 × 0.6 × 0.79 × 0.75 × 1/log2(8) = **0.036** |
| C | No path | **0** |

Ties fall back to "likely to raise soon", then the most recent round, then the name
([reports/rank.py](../backend/app/reports/rank.py)).

## Trust: from `source_rank` to a badge

Every value on screen is a `Fact` with its source and trust level. A fact with several
sources shows the strongest; the score uses the weakest edge of a path, so Grabbit never
claims more trust than Cala states ([agent.md](agents/agent.md)).

```mermaid
flowchart LR
  subgraph Cala
    SR["source_rank on each<br/>property and edge"]
  end
  SR --> F["Official filing<br/>registries, regulators"]
  SR --> P["Company or investor<br/>primary source"]
  SR --> Pr["Press"]
  SR --> Db["Database<br/>aggregators, empty or missing rank"]
  News["Cala knowledge query<br/>'latest news regarding X'"] --> CN["Cala news"]
  Web["Context.dev"] --> WU["Web, unverified<br/>never mixed with Cala facts"]
  Absent["Field absent in Cala"] --> NP["Not published<br/>never shown as 0"]
```

Dates keep their precision: a year-only date reads "2019", never "2019-01-01".

## Self-personalization: the agent rewrites itself

The profile has structured fields (filters, reference investors, style, cadence, alert
threshold) and free-text `instructions` that Gemini writes for itself. Each turn it can call
`update_profile` or `rewrite_instructions`. If it called neither, a second pass asks whether
the reaction implies a lasting preference ([agent.md](agents/agent.md)).

```mermaid
flowchart TB
  Msg["Angel: 'Shorter, one line per startup'"] --> Turn["Gemini turn<br/>system prompt + profile + instructions + report"]
  Turn -->|tool call| UP["update_profile(patch, reason)<br/>validated by Pydantic"]
  Turn -->|tool call| RW["rewrite_instructions(text, reason)"]
  Turn -->|no tool called| Learn["learn.py: does this reaction<br/>imply a lasting preference?"]
  Learn --> RW
  RW --> Guard{"rules.py guard<br/>fixed rules kept?"}
  Guard -- no --> Reject["Rejected"]
  Guard -- yes --> V["New profile version<br/>ProfileChange: before, after, reason, by agent"]
  UP --> V
  V --> Note["Reply: 'From now on: one line per startup.'<br/>composed by the server from the applied call"]
  V --> Regen["Report regenerated,<br/>changes highlighted on screen"]
  V --> Hist["What changed: history with undo"]
```

## Proactivity: watcher, digest and alerts

Cala has no push or webhooks, so Grabbit polls and diffs, modelled on scheduled
"routines": a run remembers the last state and stays silent when nothing changed
([flow.md](agents/flow.md#4-proactive-architecture)).

```mermaid
stateDiagram-v2
  [*] --> Waiting
  Waiting --> Polling: every 15 min
  Polling --> Diffing: read shortlisted entities from Cala
  Diffing --> Waiting: nothing new
  Diffing --> Scoring: change found (new round, executive, headcount, acquisition)
  Scoring --> Waiting: below the profile's threshold
  Scoring --> Delivering: rules first, then a Gemini score with a one-line reason
  Delivering --> Waiting: SSE alert → toast + desktop notification
```

| Routine | When | What |
| --- | --- | --- |
| Watcher | Every 15 minutes | Diff the shortlist against the last snapshot, score, alert |
| Digest | Prep report, daily in the event week, weekly after | What changed and why, new matches |
| News | Every 6 hours, first run a minute after start | Cala news for the latest report's startups, cached for reports |
| Demo trigger | "Alerts" button, `DEMO_MODE=1` | A scripted change through the same diff, scoring and delivery, labelled "Simulated event" |

## Guardrails

| Risk | Guardrail | Where |
| --- | --- | --- |
| The model invents a number | Report prose cites values only as `{placeholders}`; the server renders them from sourced facts and rejects drafts with digits or unknown placeholders | [reports/write.py](../backend/app/reports/write.py) |
| The agent recommends a purchase | Fixed rules in the system prompt and a deterministic guard on `rewrite_instructions` | [agent/rules.py](../backend/app/agent/rules.py) |
| The agent claims a change it did not make | "From now on" is composed by the server from the applied tool call | [agent/chat.py](../backend/app/agent/chat.py) |
| A chart draws a walk that did not happen | Visual answers that reference unseen entities are dropped | [agent/visual.py](../backend/app/agent/visual.py) |
| Staged data mixes with real data | The demo event lives in its own fixture, never in the Cala cache | [fixtures/demo_events/](../backend/app/fixtures/demo_events/) |
| Venue wifi or Cala down | Every response cached, replay mode, `make warm --check` before a demo | [cala/client.py](../backend/app/cala/client.py) |
| The Gemini key leaks to the browser | Live transcription uses a single-use ephemeral token | [api/transcribe.py](../backend/app/api/transcribe.py) |

## Data model

```mermaid
erDiagram
  WORKSPACE ||--|| PROFILE : has
  PROFILE ||--o{ PROFILE_VERSION : "history (undo)"
  PROFILE_VERSION ||--o{ PROFILE_CHANGE : "before, after, reason, by"
  WORKSPACE ||--o{ CHAT_MESSAGE : has
  WORKSPACE ||--o{ REPORT : has
  REPORT ||--o{ CANDIDATE : ranks
  CANDIDATE ||--o{ FACT : "value + trust + source + date precision"
  CANDIDATE ||--o{ PROXIMITY_PATH : "why it is here"
  WORKSPACE ||--o{ SNAPSHOT : "per watched entity"
  WORKSPACE ||--o{ ALERT : receives
  CALA_CACHE {
    string key "method + path + body hash"
    json response
    datetime fetched_at
  }
```

The Cala and Context.dev caches are shared across workspaces; everything else is filtered
by the browser's anonymous workspace id.

## Where things live

| Part | Code | Deeper reading |
| --- | --- | --- |
| Cala client, cache, rate limit | [backend/app/cala/](../backend/app/cala/) | [agents/cala.md](agents/cala.md) |
| Event walk, reverse walk, proximity | [backend/app/discovery/](../backend/app/discovery/) | [algorithm.md](algorithm.md) |
| Fund identity | [backend/app/trusted.py](../backend/app/trusted.py) | [algorithm.md](algorithm.md#3-one-fund-one-identity-196) |
| Signals | [backend/app/signals/](../backend/app/signals/) | [agents/agent.md](agents/agent.md) |
| Agent and its tools | [backend/app/agent/](../backend/app/agent/) | [agents/agent.md](agents/agent.md) |
| Reports | [backend/app/reports/](../backend/app/reports/) | [agents/flow.md](agents/flow.md) |
| Watcher and scheduler | [backend/app/watcher/](../backend/app/watcher/), [scheduler.py](../backend/app/scheduler.py) | [agents/flow.md](agents/flow.md) |
| Web app | [frontend/src/](../frontend/src/) | [agents/frontend.md](agents/frontend.md), [DESIGN.md](../DESIGN.md) |
| API contract | [backend/app/models.py](../backend/app/models.py) | [agents/api.md](agents/api.md) |
