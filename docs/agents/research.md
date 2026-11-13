# User research

Distilled from two investor interviews and a team debrief on Fri 2026-11-13. Interviewees
are pseudonymised: never add their names, employers or other identifying details to this
repo (it is public). Raw recordings and transcripts stay outside the repo.
Full meeting minutes (Spanish, pseudonymised): `docs/research/acta-2026-11-13.md`.
Profile cards (Spanish): `docs/research/investor-a.md`, `docs/research/investor-b.md`.
Read this before deciding the target user, product behaviour, demo script or pitch.

## Interviewees
- **Investor A**: software engineer, invests his own savings as a hobby. Moved from
  short-term trading to long-term value investing; mixed portfolio (stocks, index funds,
  derivatives). Follows the market weekly, not an expert.
- **Investor B**: works at an investment fund (VC and private equity). Knows how the Cala
  team thinks. His fund is building this kind of tooling in-house.

## What Cala wants (from talking to the Cala team at the venue)
- No dashboard. Something active that reaches the user. They liked "proactive agent".
- One concrete user and one problem, not a generic tool with a nice slogan.
- Something they can show at a founders and investors event next week (a working POC).
- Two API methods that return the graph already processed by an LLM are being deprecated.
  Use the one that returns the raw graph and build on it. Confirm which one with Cala.
- Investor B on what the Cala team cares about most: (1) veracity of the data,
  (2) knowledge transfer: people are slow to learn a domain; an agent should cut that time.

## Findings
1. **The pain is real at both ends.** A: "I have no time to scout; if a tool pre-selects and
   I review each pick by hand, I've already won." B: "This is a real problem; we have it
   ourselves and are building it by hand."
2. **The AI must not decide.** Both want signals and evidence; the investor approves.
3. **Risk-profile classifiers are not a product.** Every broker already does it.
4. **Cala as the trust layer.** B: gather information from the web (reports, news, search
   tools such as Context.dev or Exa), then fact-check every number against Cala. Pitch
   angle: "who has the authority to certify a number?"
5. **Ask, don't just report (B).** The investor gives a vague thesis; the agent fires many
   questions backed by data; each answer triggers new searches, fact-checked with Cala;
   the thesis narrows sector -> subsector -> companies. Like plan mode in a coding agent:
   the machine proposes, the human takes every micro-decision. The agent knows which data
   matter per subsector; the investor does not.
6. **End output (B): an investment memo**: "I start with a subsector and end with these
   seven companies that pass my checks."
7. **Subsector characterisation used by private equity (B):** average EBITDA, fragmentation
   (how many companies, concentration by geography), regulatory tailwinds, owner and
   executive profile, succession risk. Use these as the agent's question checklist.
8. **Weekly digest (A).** Daily is too much, monthly too late. Explain *why* a holding moved
   (link it to news or the market), not just *what* moved.
9. **Sources:** always cite them, but "nobody reads them" (A). Make verification visible
   inline (e.g. "verified by Cala" vs "web, unverified"), not a link list at the end.
10. **Soft signals (A):** sentiment matters; people sell when others sell. Idea: a curated
    allow-list of market commentators, shown as "what the numbers say" vs "what the market
    feels".
11. **Follow the big fish (A, B):** large single-buyer purchases or sales signal a fund
    entering or leaving. One exit can be rebalancing; two or three is a bad sign. US fund
    holdings are public filings. Check whether Cala has them; otherwise try Context.dev.

## Who the user could be
- **VC: poor fit (B).** VCs will not change their workflow, and young companies have little
  data (competitors, past failures, founder history, exits in the sector).
- **Private equity, mid-market (buying SMEs): strong fit (B).** No such workflow today and
  they need it. Companies have years of public accounts, so there is data. Information is
  scattered: company registries give revenue but not headcount, customers or shareholders.
  A sourcing process can take a deal team three months, and an external due diligence costs
  around EUR 150k: better pre-screening means more due diligences end in an acquisition.
- **Hobby investor with capital, no research team (A): volume, smaller ticket.** Needs a
  simple layer that works with a vague description; power users can tune it.
- B's advice: pick an investor type the team understands. Ticket (PE) vs volume (hobby):
  the same engine can serve both at different depths.
- Decision pending: see `decisions.md` and challenge.md "Who the user is".

## Product ideas gathered
- Onboarding by conversation, then tuning by chat ("stop sending me construction").
- Proactive delivery: weekly digest plus alerts. POC sends to an in-app chat; keep the
  interface ready for Telegram or WhatsApp and say so in the pitch.
- Pitch metric: more companies analysed in the same time, with wider context than a person
  juggling browser tabs.

## Business model ideas (for the pitch, B)
- Commission only on analyses that end in a purchase.
- Upsell for hobby investors: "what did reference investor X do in situation Y", per query.
- Include the business view in the pitch even if not required: B's team won a previous
  hackathon partly because of it.

## Pitch and video notes (team)
- Opening scene: a stressed investor lost in browser tabs and charts asks a generic chatbot
  "which startup should I invest in?" and gets a useless answer.
- Message: the tool does not stop you being wrong; it helps you decide better.
- State in the README and pitch that the product was shaped by interviews with real
  investors (pseudonymised).

## Open questions
- Does Cala's graph cover private mid-market companies, fund holdings and transactions, or
  mostly startups and funding rounds? This decides the user and the "big fish" feature.
- Will Cala object to Context.dev as a second source? Ask them. Context.dev also has its own
  challenge, so using it well may qualify for a second prize.
- More interviews requested via a community post; add new findings here.
