# Pitch, deck and submission

Draft material for the README, the 2-minute peer review at the table, the deck PDF and the
final pitch. Everything marked "draft" needs a human to confirm. Facts come from
research.md and cala.md; never add figures that are not sourced there.
The video script lives in challenge.md "Demo script".

## Punchline (chosen 2026-11-14, identical in README and form)
"Slush has 2,989 attendees and you are one person. Grabbit finds the startups backed by
the investors you trust, shows the source of every fact, and alerts you when one of them
moves."

## Problem (sourced)
- User: an investor who decides alone and has neither the time nor the means to build
  automated research systems, from small private equity down (challenge.md "Who the user
  is"). The demo follows a business angel preparing Slush 2026.
- The angel's number: Slush 2026 has 2,989 attendees in Cala (2,980 companies), against one
  person. Source: warm-up of 2026-11-14 (issue #30); rerun `make warm` before quoting it.
- Same pain higher up the segment: a PE sourcing process can take three months and an
  external due diligence costs around EUR 150k (Investor B, research.md). Use as backup,
  not as the headline.
- Individual investor with capital: no time to scout new opportunities (Investor A).
- Web information is scattered and unverifiable: "who certifies a number?" (Investor B).

## Solution (draft, follows the MVP in challenge.md)
An agent that starts from a vague thesis, walks the Slush 2026 attendees in Cala's graph,
asks data-backed questions, narrows them to a shortlist and a memo, and then watches those
startups before, during and after the event until the angel finds a round. Every fact
shows its trust level and source; web signals are labelled "web, unverified". The agent
personalizes the report itself from the conversation, rewriting its own instructions. It
never tells you what to buy.

## Why Cala is core (Use of Cala, 25%)
- Every fact on screen comes from Cala's raw entity graph with source and date (cala.md).
- The agent reads each entity's introspection, so its questions grow with Cala's coverage
  (decisions.md).
- Discovery from the graph: the Slush 2026 `Event` lists its attendees; the web only adds
  colour (decisions.md 03:10).
- Signals only the graph gives: who led and co-invested in each round (`is_lead`),
  "co-invest with who you trust", "likely to raise soon" from dated headcount and rounds.
- Trust level per fact from `source_rank`, with date precision (cala.md).
- The watcher diffs Cala's dated edges (rounds, executives, headcount, acquisitions).
- Pitch line: Cala's graph finds the deal; every fact shows how much you can trust it.

## Originality (draft)
- Headline: the agent personalizes itself. Every correction or reaction in the chat makes
  Gemini rewrite its own report instructions; the report changes on screen and the history
  shows what it learned (agent.md "Self-personalization").
- An agent that asks the investor questions instead of only answering them (Investor B's
  "plan mode" analogy).
- Trust as the product: every fact shows how strong its source is (registry, company,
  press, database) and how precise its date is; "not published" is never shown as zero.
- Meet startups before their round: "likely to raise soon", not "raised last month".
- To research before claiming anything (R6 in open-questions.md): startup databases with
  saved searches and alerts (Harmonic, Specter, Crunchbase, Dealroom), generic AI chatbots.
  State the difference, not "nothing like it exists".

## Impact and implementation (event-wide judges, draft)
- Impact: many angels and small investors decide without a research team; the same engine
  serves any event in Cala or a free thesis, and small funds at a deeper level.
- Implementation: built only on public, sourced data via API; costs and data freshness are
  open questions (open-questions.md C2, C6); state them honestly.

## Business model (draft, must not contradict decisions.md)
- Options consistent with "the investor decides": subscription per seat, per memo, or per
  watched company. Commission on executed deals only as future work, without the bot buying
  (open-questions.md K1).
- Upsell idea for individuals: "what did reference investor X do in situation Y", per query
  (Investor B), depends on C7.

## 2-minute table script for peer review (draft)
1. 0:00-0:20 Problem in one sentence plus one number (Slush attendees vs one person).
2. 0:20-1:20 Live: type a vague thesis and two reference investors, answer two questions,
   see the Slush shortlist with leads and trust levels; say "shorter, co-investors first"
   and watch the report change; open one source.
3. 1:20-1:45 Trigger the simulated event; the alert explains why it matters.
4. 1:45-2:00 Punchline and what is next (messaging channels, more events as Cala grows).

## Deck outline (PDF, about 8 slides)
1. Name, punchline, team.
2. Problem and user, with the two interview quotes (pseudonymised).
3. Solution: the flow in one picture.
4. Demo screenshots: thesis -> questions -> shortlist -> memo -> alert.
5. Why Cala: discovery from the Slush event, round leads, trust level per fact.
6. Validation: interviews with two investors.
7. Business model and what is next.
8. Technologies and links (demo, repo, video).

## Submission checklist (challenge.md "Submission form needs")
- [ ] Punchline chosen and identical in README and form.
- [ ] README: Problem, Solution, Demo links, Technologies used, Team roles.
- [ ] Video max 2:00, public on YouTube or Vimeo, simulated event labelled.
- [ ] Deployed demo link works from a clean browser.
- [ ] Deck PDF uploaded.
- [ ] Repo public, MIT licence, link in the form.
- [ ] Credit choice, phone numbers, Discord usernames.
- [ ] Status switched from DRAFT to FINAL before Sun 10:00.
- [ ] All four present for peer review from Sun 10:30.
