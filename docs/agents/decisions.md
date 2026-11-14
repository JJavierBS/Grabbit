# Decisions

Check here before re-opening a question. Append one line per decision, newest last.
Format: `YYYY-MM-DD HH:MM | area | decision | why`
2026-11-13 22:30 | product | Name: Grabbit | grab the company you want + research rabbit holes
2026-11-13 22:30 | product | Proactive agent, no dashboard | Cala asked for it; both interviewed investors agree
2026-11-13 22:30 | product | The agent never recommends what to buy; the investor decides | both investors want evidence, not decisions
2026-11-13 22:30 | data | Cala is the verified source; web search (Context.dev) only adds unverified soft signals | Cala judges value data veracity; see research.md
2026-11-13 22:30 | data | Use Cala's raw-graph method, not the LLM-processed ones being deprecated | Cala team request
2026-11-13 23:55 | docs | Raw briefs and vendor docs are versioned in docs/reference/ (mirrors via scripts/fetch-docs.sh); agents read a distilled docs/agents/<vendor>.md first | whole team and every agent get the full source on clone without browsing
2026-11-14 01:35 | data | The agent reads Cala introspection per entity and only asks about fields that exist; missing fields are shown as unverified or unavailable | coverage differs by country today and will grow, so the product improves without code changes
2026-11-14 01:38 | product | User: an investor with neither the time nor the means to build automated research systems, who needs to maximise the output of their time; fund type and size are examples, not the definition | both interviewed investors fit (one has the skills but not the time, the other builds by hand because most cannot); matches the demo hook of spending energy on deciding, not researching
2026-11-14 02:17 | product | Demo video spine: overwhelmed investor, onboarding with corrections, first report validated, urgent portfolio alert after he leaves; script in challenge.md | shows the proactive agent Cala asked for and the time-saving hook in under 2 minutes
2026-11-14 02:17 | product | Urgent alerts reach the user as browser desktop notifications; Telegram or WhatsApp only in the pitch | cheapest channel that works on the demo laptop; the delivery interface keeps other channels open
2026-11-14 02:17 | product | The thesis-to-memo flow stays in the MVP, shown live and in Q&A, not in the video | it is the deepest use of Cala; the video has no room for it
2026-11-14 02:17 | architecture | Proactivity via scheduled routines (digest, watcher) that poll Cala and diff against snapshots, modelled on OpenMausBot; see flow.md | Cala has no push or webhooks; diffing lets each run report only what is new
2026-11-14 02:19 | product | The demo mocks the watcher query: a scripted change triggers the alert through the real importance check and delivery path; the portfolio uses an existing company | the video needs the alert seconds after validation, which a real poll cannot guarantee
2026-11-14 02:45 | product | Segment: investors from small private equity down who cannot build automated research. Demo persona: a business angel investing in startup rounds; supersedes the search-fund proposal (open-questions D3) | Cala asked for one concrete problem; an angel fits the track (rounds, investors) and Cala's funding-round graph. Overrides Investor B's advice against startups (thin data): see open-questions R8
2026-11-14 02:45 | product | One flow: thesis -> data-backed questions -> shortlist -> proactive reports on that shortlist until the investor finds the company. Watching a portfolio of listed shares is dropped; supersedes the 02:17 video spine's portfolio alert | Cala asked for focus; one need solved well beats two halfway (brief)
2026-11-14 02:45 | product | Differentiator: the agent adapts to each investor and the investor configures it (criteria, sources, format, alert threshold) | what databases with fixed screens and alerts do not offer
2026-11-14 02:45 | product | Hero signal from Cala's funding-round graph (lead investors and co-investors of similar companies, round dates) instead of succession risk | succession risk only applies to mature SMEs, not to startups
2026-11-14 02:45 | data | Country coverage is not a product constraint; the demo picks companies where Cala has data | Cala is the audience to impress and its coverage keeps growing
2026-11-14 02:45 | product | Alert triggers are chosen when the demo is recorded | depends on which real events exist for the demo companies (open-questions R3)
