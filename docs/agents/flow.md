# App flow

The ideal user flow and the proactive architecture behind it. Read this before building
onboarding, reports, alerts or the chat, or before turning them into issues. The demo video
script lives in challenge.md "Demo script"; this file is the product it shows.
Keep this file under 100 lines.

## 1. Onboarding (first launch, text or voice)
A conversation, not a form. The user can end it at any moment; every unanswered field takes
a default, so the first report can always run. Ask in this order (most needed first):
1. Thesis: what they look for, in their own words, however vague (sector, stage, ticket),
   and the event if any (default Slush 2026). The thesis flow narrows it later (section 3).
2. Reference investors they trust (funds or angels) and companies they already know,
   optional. Resolve each name to a Cala entity and confirm it ("X Ventures, Helsinki?").
   Unresolved names stay as web-only.
3. Sectors to include or exclude.
4. Preferred sources: commentators, media or influencers. They form the allow-list read
   through Context.dev, labelled "web, unverified" (research.md finding 10).
5. Investment profile: one question, used as context. Not a feature (finding 3).
6. Format: length, level of detail, alert threshold. Cadence follows the event (agent.md
   "Cadence"). Ask lightly or skip: the first report is the better place to tune format.
Corrections ("no B2C", "less technical") update the profile immediately: Gemini edits the
profile and its own report instructions (agent.md "Self-personalization"). Questions come
from the question bank in agent.md.
Voice input: browser speech-to-text into the same chat; nice to have.

## 2. First report (validation)
- Runs as soon as onboarding ends, on real data, in the final format: the event prep
  report. Candidates are the event's attendees in Cala (`Event` -> incoming
  `PARTICIPATES_IN_EVENT`, cala.md), filtered locally by founding date, funding stage and
  headcount to drop funds and corporates. Per startup: last rounds with lead and
  co-investors, overlap with the reference investors, "likely to raise soon" (signal
  definitions: agent.md).
- Every fact shows its trust badge (agent.md "Trust scale") and its date precision; an
  absent field reads "not published", never zero.
- The user reacts ("shorter", "drop construction"); each reaction edits the profile and the
  report is regenerated. Loop until the user confirms.
- Confirmation schedules the recurring digest and starts the watcher. The browser asks for
  notification permission here, so alerts can reach the user later.

## 3. Steady state
- Scheduled digest (daily in the event week, weekly after): what changed in the shortlist and
  why (a new round, who led it, news), new candidates that match the thesis, soft signals
  apart. Facts carry their trust level, web items "web, unverified", inline. Nothing new:
  a one-line message or none. Around the event: prep before, alerts during, follow-up
  after, until the angel finds a round.
- Urgent alert, outside the schedule: see section 4. Arrives as a desktop notification;
  clicking it opens the chat with the detail and its sources.
- Chat at any time: follow-up questions and tuning, which update the profile. The chat runs
  the thesis flow (vague thesis, data-backed questions, shortlist, memo; challenge.md
  "Scope"). The agent never recommends what to buy.

## 4. Proactive architecture
Modelled on OpenMausBot's "routines" (github.com/milind-soni/OpenMausBot): scheduled runs,
polling for events, memory of the last run, and silence when there is nothing new. We
reuse the concepts, not the code.

| Part | Role |
| --- | --- |
| Profile store | Onboarding answers, thesis, shortlist as Cala entity ids, format, threshold, Gemini's own `instructions`, versions |
| Scheduler | APScheduler in the API process (architecture.md). Two routines per user: `digest` (from the cadence) and `watcher` (every 15 min). A run is skipped while the previous one is still active |
| Snapshot store | Last known state per watched entity and the last report sent. Each run receives them, so it reports only what is new and can explain the change |
| Watcher | Cala has no push or webhooks: poll the watched entities, diff against the snapshot |
| Importance check | Explicit rules first, then an LLM score with a one-line reason; alert only above the user's threshold |
| Delivery channel | In-app chat plus browser desktop notification via `/api/events`; Telegram and WhatsApp are out of scope (may be named as future in the pitch) |

What the watcher diffs in Cala (cala.md): a new `FundingRound` and its lead; an executive
joining or leaving (`valid_since`/`valid_until` on `IS_CEO_OF`, `IS_CTO_OF`...); a
headcount jump (`employee_count` series); an acquisition (`CorporateEvent`); a domain
turning `INACTIVE` or a change in `operational_status`. From the web: news about a
shortlisted startup (unverified unless Cala confirms it). The demo picks one when recording.
Alert hygiene: dedupe per entity and event, cap alerts per day, queue them while the user
is mid-conversation.

## 5. What the demo needs from the build
- A "run now" for the digest and a demo trigger for the watcher: the video shows an alert
  seconds after the first report, which a real poll cannot guarantee. The watcher query is
  mocked for the demo (team decision): the trigger feeds a scripted change into the same
  diff, importance check and delivery path the real watcher uses. The scripted change lives
  in its own fixture loaded by a "simulate event" action, never in the Cala response cache,
  so staged data stays separate from real data and can be shown if a judge asks.
- The demo shortlist: real Slush 2026 AI startups at pre-seed and seed; staged alert
  `grei_seed_round` (decisions.md 2026-11-14 09:40).
- The Slush attendee list and the demo path pre-warmed in the cache (architecture.md
  "Constraints"); Cala will raise the rate limit, the cache is for resilience.
- The Grabbit tab stays open in the browser so desktop notifications fire.
