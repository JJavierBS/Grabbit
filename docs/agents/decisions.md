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
