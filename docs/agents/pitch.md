# Pitch, deck and submission

Draft material for the README, the 2-minute peer review at the table, the deck PDF and the
final pitch. Everything marked "draft" needs a human to confirm. Facts come from
research.md and cala.md; never add figures that are not sourced there.
The video script lives in challenge.md "Demo script".

## Punchline (draft, pick one, max one sentence)
- "Grabbit turns a vague investment thesis into a verified shortlist, and tells you when
  something changes."
- "Spend your time deciding, not researching: an investing agent where every fact is
  verified by Cala."
- "The research team small investors cannot afford: it asks the right questions, checks
  every number and watches your companies for you."

## Problem (sourced)
- User: an investor who decides alone and has neither the time nor the means to build
  automated research systems (challenge.md "Who the user is").
- Small private equity: a sourcing process can take a deal team three months; an external
  due diligence costs around EUR 150k, so better pre-screening means more due diligences end
  in an acquisition (Investor B, research.md).
- Hobby investor with capital: no time to scout new opportunities; already built a weekly
  portfolio digest by hand (Investor A).
- Web information is scattered and unverifiable: "who certifies a number?" (Investor B).

## Solution (draft, follows the MVP in challenge.md)
An agent that starts from a vague thesis, asks data-backed questions, narrows it to a
shortlist and a memo, and then watches those companies. Every fact is labelled "verified by
Cala" with its source; web signals are labelled "web, unverified". It never tells you what
to buy.

## Why Cala is core (Use of Cala, 25%)
- Every fact on screen comes from Cala's raw entity graph with source and date (cala.md).
- The agent reads each entity's introspection, so its questions grow with Cala's coverage
  (decisions.md).
- The watcher diffs Cala's dated edges (rounds, ownership, filings) to detect change.
- Pitch line: the web finds candidates; Cala decides what is true.

## Originality (draft)
- An agent that asks the investor questions instead of only answering them (Investor B's
  "plan mode" analogy).
- Verification as the product: every claim carries "verified by Cala" or "web, unverified".
- To research before claiming anything (R6 in open-questions.md): investment databases with
  alerts, generic AI chatbots, broker robo-advisors and risk classifiers (already common,
  Investor A). State the difference, not "nothing like it exists".

## Impact and implementation (event-wide judges, draft)
- Impact: many investors make decisions without a research team; the same engine serves
  small funds (high value per user) and individuals (volume) at different depths.
- Implementation: built only on public, sourced data via API; costs and data freshness are
  open questions (open-questions.md C2, C6); state them honestly.

## Business model (draft, must not contradict decisions.md)
- Options consistent with "the investor decides": subscription per seat, per memo, or per
  watched company. Commission on executed deals only as future work, without the bot buying
  (open-questions.md K1).
- Upsell idea for individuals: "what did reference investor X do in situation Y", per query
  (Investor B), depends on C7.

## 2-minute table script for peer review (draft)
1. 0:00-0:20 Problem in one sentence plus one number (3 months, EUR 150k).
2. 0:20-1:20 Live: type a vague thesis, answer two questions, see the shortlist with
   "verified by Cala" labels; open one source.
3. 1:20-1:45 Trigger the simulated event; the alert explains why it matters.
4. 1:45-2:00 Punchline and what is next (Telegram or WhatsApp, more countries as Cala grows).

## Deck outline (PDF, about 8 slides)
1. Name, punchline, team.
2. Problem and user, with the two interview quotes (pseudonymised).
3. Solution: the flow in one picture.
4. Demo screenshots: thesis -> questions -> shortlist -> memo -> alert.
5. Why Cala: verified facts, introspection, dated edges.
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
