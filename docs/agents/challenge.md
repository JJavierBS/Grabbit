# Challenge

Distilled from the raw briefs in `docs/reference/` and `material/` (local, not versioned). Agents read this
file, not the raw PDFs or slides. Keep it under 100 lines. All times Europe/Helsinki (UTC+2).

## Track
- Challenge and partner: "Make Unicorns Real" by Cala. Raw brief: `docs/reference/cala-track-brief.md`.
- Problem: founders and investors decide on scattered, stale information (tabs, old
  databases, gut feeling). Build a product on Cala's structured, sourced data (companies,
  people, funding rounds, investors and the links between them) that solves one real need
  for founders, investors or both. Focus beats breadth. Target: usable at Slush, right after.
- Who the user is: TODO (pick one concrete user, e.g. a first-time founder raising a seed).
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

## Cala API (docs.cala.ai, checked 2026-11-13)
- Base `https://api.cala.ai`, header `X-API-KEY: $CALA_API_KEY` (keys: console.cala.ai/api-keys).
- Credits: console.cala.ai, Billing > Extra credits > Add credits > promo code MAKEUNICORNSREAL.
- `POST /v1/knowledge/search`: natural-language answer in markdown, with citations.
- `POST /v1/knowledge/query` with `{"input": "..."}`: structured rows plus entities. Takes
  natural language or Cala QL, e.g. `startups.location=Spain.funding>10M.funding<=50M`.
- `/v1/entities` fuzzy name search; `/v1/entities/lookup` by identifier (LEI, CIK...);
  `/v1/entities/{id}` full entity. Types include Company, Person, FundingRound.
- Errors: 422 validation, 429 rate limit. Cache responses: the demo must survive bad wifi.
- MCP: `https://api.cala.ai/mcp/`, same header. Claude Code:
  `claude mcp add --transport http cala https://api.cala.ai/mcp/ --header "X-API-KEY: <key>"`

## Event-wide judging (peer review and final judges)
- Innovation: new or different compared to the other projects.
- Impact: significant for society; solves it for a large share of the people affected.
- Implementation: realistic, viable and feasible from every perspective.
Peer review happens at tables: a stranger must get the point and see it work in ~2 minutes.

## Rules that affect the code
- All project code is written during the event (from Fri 19:30). Open source libraries are fine.
- Submission is MIT-licensed and the source must be accessible: the repo is public.
- Partner APIs and data stay under the partner's terms; Cala usage limits: TODO (ask at the workshop).

## Deadlines
- Fri 23:59: pre-submission draft on Junction Platform with the chosen challenge.
- Sat 12:00: submissions open.
- Feature freeze: TODO (team decides).
- Sun 10:00: final submission. Form closes automatically; DRAFT projects are not reviewed.
- Sun 10:30-13:00: live peer review; all 4 present or no main prize.
- Top 5: 3 min pitch with live demo from our own laptop, then 3 min questions.

## Submission form needs
Project name, punchline, description, challenge, technologies used, pitch video (max 2:00,
strictly; public on YouTube/Vimeo), demo link, source link, source publicity, credit choice,
pitch deck PDF, team phone numbers and Discord usernames. README.md mirrors the text fields.

## Partner tech on site (check each track's terms)
Google DeepMind (Gemini), NVIDIA, Verda, Modal (GPU/compute), Exa (search API), Cala
(company/investor data, "Make Unicorns Real"), Hostinger (hosting), Arduino and Intel
(hardware lab), MLH x GitHub.
Hackerpack we may use: Context.dev web data API (companies, people, news, scrape), 50k
credits per team; see `context-dev.md`.

## Scope
- MVP (must demo): TODO
- Nice to have: TODO
- Explicitly out of scope: TODO

## Demo script
TODO: the 5-7 steps shown live, in order. Features not in this list are low priority.
