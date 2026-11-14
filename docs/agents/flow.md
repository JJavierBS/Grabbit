# App flow

The ideal user flow and the proactive architecture behind it. Read this before building
onboarding, reports, alerts or the chat, or before turning them into issues. The demo video
script lives in challenge.md "Demo script"; this file is the product it shows.
Keep this file under 100 lines.

## 1. Onboarding (first launch, text or voice)
A conversation, not a form. The user can end it at any moment; every unanswered field takes
a default, so the first report can always run. Ask in this order (most needed first):
1. Mode: watch my portfolio, explore sectors, or both.
2. Holdings: listed shares and startup stakes. Resolve each name to a Cala entity and
   confirm it with the user ("X Ltd, London?"). Unresolved names stay as web-only.
3. Sectors of interest.
4. Preferred sources: commentators, media or influencers. They form the allow-list read
   through Context.dev, labelled "web, unverified" (research.md finding 10).
5. Investment profile: one question, used as context. Not a feature (finding 3).
6. Format: frequency (default weekly, finding 8), length, level of detail, alert threshold.
   Ask lightly or skip: the first report is the better place to tune format.
Corrections ("no, I sold that", "less technical") update the profile immediately.
Voice input: browser speech-to-text into the same chat; nice to have.

## 2. First report (validation)
- Runs as soon as onboarding ends, on real data, in the final format.
- The user reacts ("shorter", "drop construction"); each reaction edits the profile and the
  report is regenerated. Loop until the user confirms.
- Confirmation schedules the recurring digest and starts the watcher. The browser asks for
  notification permission here, so alerts can reach the user later.

## 3. Steady state
- Scheduled digest, at the chosen frequency: what changed in the holdings and why (link a
  move to news or the market, not only what moved), sector news, soft signals apart. Facts
  are labelled "verified by Cala", web items "web, unverified", inline. Nothing new: a
  one-line message or none.
- Urgent alert, outside the schedule: see section 4. Arrives as a desktop notification;
  clicking it opens the chat with the detail and its sources.
- Chat at any time: follow-up questions and tuning, which update the profile. In explore
  mode the chat runs the thesis flow (vague thesis, data-backed questions, shortlist, memo;
  challenge.md "Scope"). The agent never recommends what to buy.

## 4. Proactive architecture
Modelled on OpenMausBot's "routines" (github.com/milind-soni/OpenMausBot): scheduled runs,
polling for events, memory of the last run, and silence when there is nothing new. We
reuse the concepts, not the code.

| Part | Role |
| --- | --- |
| Profile store | Onboarding answers, holdings as Cala entity ids, format, threshold |
| Scheduler | Two routines per user: `digest` (cron from the profile) and `watcher` (every ~15 min). A run is skipped while the previous one is still active |
| Snapshot store | Last known state per watched entity and the last report sent. Each run receives them, so it reports only what is new and can explain the change |
| Watcher | Cala has no push or webhooks: poll the watched entities, diff against the snapshot |
| Importance check | Explicit rules first, then an LLM score with a one-line reason; alert only above the user's threshold |
| Delivery channel | One interface: in-app chat plus browser desktop notification now; Telegram or WhatsApp later (say so in the pitch) |

What the watcher can diff in Cala (cala.md): new `PARTICIPATES_IN_CORPORATE_EVENT` edges
(funding rounds, with `event_date`), ownership edges with `valid_since`/`valid_until`
(UK), new filed accounts and metric values. From the web: adverse news about a holding, a
followed fund buying or selling (finding 11, unverified unless Cala confirms it).
Alert hygiene: dedupe per entity and event, cap alerts per day, queue them while the user
is mid-conversation.

## 5. What the demo needs from the build
- A "run now" for the digest and a demo trigger for the watcher: the video shows an alert
  seconds after the first report, which a real poll cannot guarantee. The watcher query is
  mocked for the demo (team decision): the trigger feeds a scripted change into the same
  diff, importance check and delivery path the real watcher uses.
- The demo portfolio uses an existing company (team picks it).
- Responses for the demo path pre-warmed in the cache (architecture.md "Constraints").
- The Grabbit tab stays open in the browser so desktop notifications fire.
