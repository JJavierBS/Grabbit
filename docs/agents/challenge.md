# Challenge

Distilled from the raw briefs in `docs/reference/` and `material/` (local, not versioned). Agents read this
file, not the raw PDFs or slides. Keep it under 100 lines. All times Europe/Helsinki (UTC+2).

## Track
- Challenge and partner: "Make Unicorns Real" by Cala. Raw brief: `docs/reference/cala-track-brief.md`.
- Problem: founders and investors decide on scattered, stale information (tabs, old
  databases, gut feeling). Build a product on Cala's structured, sourced data (companies,
  people, funding rounds, investors and the links between them) that solves one real need
  for founders, investors or both. Focus beats breadth. Target: usable at Slush, right after.
- Who the user is: an investor who makes their own decisions and has neither the time nor the
  means to build automated research systems, so every hour spent researching is an hour not
  spent deciding. They need to get the most out of their time. Segment: from small private
  equity down (search funds, business angels, individual investors). The demo follows one
  business angel preparing Slush 2026, with one thesis (research.md, decisions.md).
- Partner judging, 25% each, in their words:
  - Real need: a clear user with a problem worth solving.
  - Execution: it works smoothly, end to end.
  - Originality: a fresh angle, even on a familiar problem.
  - Use of Cala: Cala is core to the product, not an add-on.
- Partner idea seeds (starting points, not a menu): lead investors still actively investing
  in companies like yours; reading a market (competitors, recent rounds and from whom,
  funding flow per industry); spotting young companies early or a sourced background check
  before investing; first customers among freshly funded companies, market sizing with real
  company data, likely acquirers. Needs they have not thought of are welcome.
- Must use: Cala API or MCP as the core data source. Must not use: none stated.
- Cala on site: CTO Issey Masuda and engineers as mentors; contact Elies Delgado,
  elies@cala.ai. Workshop "Tips & tricks to Make Unicorns Real", Sat 11:00 (judging hints).

## Cala API
- Endpoints, response shapes, graph edges, quirks, rate limits and traversal flow:
  `docs/agents/cala.md`. Coverage per country: research.md "Cala coverage".
- Base `https://api.cala.ai`, header `X-API-KEY: $CALA_API_KEY` (keys: console.cala.ai/api-keys).
- Credits: console.cala.ai, Billing > Extra credits > Add credits > promo code MAKEUNICORNSREAL.
- Build on the entity endpoints (`/v1/entities...`), not on the LLM-processed
  `/v1/knowledge/search` and `/v1/knowledge/query` (decisions.md).
- 429 rate limit is easy to hit. Cache responses: the demo must survive bad wifi.

## Event-wide judging (peer review and final judges)
- Innovation: new or different compared to the other projects.
- Impact: significant for society; solves it for a large share of the people affected.
- Implementation: realistic, viable and feasible from every perspective.
Peer review happens at tables: a stranger must get the point and see it work in ~2 minutes.

## Rules that affect the code
- All project code is written during the event (from Fri 19:30). Open source libraries are fine.
- Submission is MIT-licensed and the source must be accessible: the repo is public.
- Partner APIs and data stay under the partner's terms; Cala usage limits: undocumented, see
  cala.md "Rate limits and latency" (ask at the workshop).

## Deadlines
- Fri 23:59: pre-submission draft on Junction Platform with the chosen challenge.
- Sat 12:00: submissions open.
- Feature freeze: TODO (team decides).
- Sun 10:00: final submission. Form closes automatically; DRAFT projects are not reviewed.
- Sun 10:30-14:00: live peer review (guidebook p. 7); all 4 present or no main prize.
- Top 5: 3 min pitch with live demo from our own laptop, then 3 min questions.

## Submission form needs
Project name, punchline, description, challenge, technologies used, pitch video (max 2:00,
strictly; public on YouTube/Vimeo), demo link, source link, source publicity, credit choice,
pitch deck PDF, team phone numbers and Discord usernames. README.md mirrors the text fields.

## Partner tech on site (check each track's terms)
Google DeepMind (Gemini), NVIDIA, Verda, Modal, Exa, Cala, Hostinger, Arduino, Intel, MLH x GitHub.
Context.dev: hackerpack (50k credits, `context-dev.md`) and its own challenge, "Web Is Your
Real-Time Database"; one submission may enter several (open-questions.md D6).

## Scope
- MVP (must demo), one flow: a proactive agent takes a vague thesis, walks the Slush 2026
  attendees in Cala's graph, asks data-backed questions and returns a shortlist and a memo,
  then keeps sending reports and alerts on it until the angel finds a round. Each fact shows
  its trust level (Cala `source_rank`: registry, company, press, database). Signals: lead
  and co-investors of each round, "co-invest with who you trust", "likely to raise soon".
  Context.dev adds soft signals ("web, unverified"). The investor configures it.
- Steps: conversational onboarding, first report validated, scheduled digest and urgent
  alerts on the shortlist by desktop notification. Full flow: `flow.md`, decisions.md.
- Nice to have: voice input in onboarding and chat; Telegram or WhatsApp channel.
- Out of scope: recommending what to buy or executing trades (decisions.md); watching a
  portfolio of listed shares; regulatory data from Cala. Rest: TODO (open-questions D7).
- Undecided points and conflicts: `open-questions.md`. Pitch, deck, README: `pitch.md`.

## Demo script
Video, max 2:00 (times approximate). Features not in this list are low priority.
1. 0:00-0:15 A business angel preparing Slush drowns in open tabs and the attendee list;
   however much time they spend, they find little of value and have no energy left to judge.
2. 0:15-0:20 They open Grabbit and close every other tab.
3. 0:20-0:55 Onboarding by conversation: a vague thesis, two reference investors, two or
   three data-backed questions and corrections.
4. 0:55-1:15 The Slush prep report: a shortlist with who led each round, co-investors they
   trust and "likely to raise soon"; each fact shows its trust level. They open one source.
5. 1:15-1:25 They leave the computer.
6. 1:25-1:40 Seconds later, an urgent desktop notification (simulated event, labelled on
   screen; open-questions.md R2) about a shortlisted startup, e.g. a new round or an
   executive leaving. They come back, read why it matters and can act on it.
7. 1:40-2:00 Voice-over pitch: Grabbit saves your time, lets you focus on deciding, and
   tells you when something changes.
The live demo and Q&A go deeper into the thesis questions and the memo.
