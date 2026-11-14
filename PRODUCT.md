# Product

<!-- impeccable:product-schema 1 -->

> Source: the Team 4 plan (`docs/plans/team-4-frontend.md`) and the product docs in
> `docs/agents/`. No separate interview took place. Lines marked *(inferred)* come from
> those docs and need a human check.

## Platform

web

## Users
- Primary: a business angel who prepares for Slush 2026. They make their own investment
  decisions and have neither the time nor the means to build automated research systems.
  Every hour of research is an hour not spent deciding.
- Segment: from small private equity down (search funds, business angels, individual
  investors). The demo follows one angel with one thesis.
- Second audience: the judges and the Cala team at a founders and investors event. They see
  the screen for seconds, often on a projector.

## Product Purpose
Grabbit is a proactive research agent. It takes a vague thesis, walks the Slush 2026
attendees in Cala's entity graph, asks two or three data-backed questions, and returns a
shortlist and a memo. After that it keeps sending reports and alerts on the shortlist until
the angel finds a round. Success: the angel spends their time on deciding, not on research.

## Positioning
- The report personalizes itself through the conversation. There is no settings screen.
  The agent rewrites its own instructions ("From now on: co-investors first.") and the
  report changes in front of the user. The profile history shows what the agent rewrote
  and why.
- Every fact shows how much to trust it, from Cala's source rank: official filing,
  company or investor, press, database, web unverified, not published.
- It reaches the user (digest, urgent alerts as desktop notifications). It is not a
  dashboard the user must visit.

## Operating Context
- One screen: a centred chat. A report shows in the chat as an outline and opens in a side
  panel (full screen on a phone). Alerts arrive as toasts and as desktop
  notifications when the tab is hidden.
- Used on a laptop while the angel plans the event, and shown on a 1920x1080 projector and
  at 375px on a phone during judging.
- Demo path: thesis -> questions -> shortlist -> rewrite -> alert (challenge.md "Demo
  script").

## Capabilities and Constraints
- Data: Cala entity graph (companies, people, funding rounds, investors). Soft web signals
  from Context.dev are always labelled "web, unverified" and kept apart from Cala facts.
- The agent never recommends what to buy. It shows signals and evidence; the investor
  decides.
- Absent data is "not published", never 0. Dates show only their precision ("2019").
- Simulated events are labelled "simulated event" on screen.
- No auth in the MVP; each browser gets its own anonymous workspace. Stack: React 18 + TypeScript + Vite, TanStack Query
  (frontend.md).

## Brand Commitments
- Name and mark: Grabbit. Grabbit keeps its own name and its own mark.
- Pinned reference aesthetic: the Grabbit logo (black, night ink #0e111a, violet #6139f8),
  a minimal chat in the manner of Grok, and reports that show as an outline in the chat and
  open in a side panel, in the manner of Claude artifacts. This replaced the cala.ai tone on
  2026-11-14 (#53). The brief wins over the design skill's own taste.
- Never use Cala's logo, wordmark or copy. Never make Grabbit look like a Cala product.
- Voice: plain, factual, short. The agent states changes in one line. *(inferred from
  agent.md and research.md)*

## Evidence on Hand
- Two pseudonymised investor interviews (`docs/agents/research.md`). Never add names or
  identifying details.
- No testimonials, customer logos, metrics or press exist. Do not invent them.

## Product Principles
1. The AI does not decide. It proposes with evidence; the investor approves.
2. Trust is visible inline, on every fact, not in a link list at the end.
3. Show the change. When the agent learns, the report visibly rewrites itself.
4. Never a blank screen. Every view has loading, empty and error states.
5. Focus beats breadth: one flow, one primary action at a time.

## Accessibility & Inclusion
- WCAG AA text contrast, visible focus on every interactive element (styles.md).
- Motion only to explain a state change, under 300ms, and respect reduced motion.
- Layout works at 375px and 1920x1080.
