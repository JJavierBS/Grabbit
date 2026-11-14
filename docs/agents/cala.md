# Cala API (entity graph)

Cala is the core data source (challenge.md). The Cala team asked us to build on the entity
endpoints, which return the raw graph, and not on the two LLM-processed ones
(`/v1/knowledge/search`, `/v1/knowledge/query`), which lose information and are being
deprecated (decisions.md). One exception, suggested by Cala at its workshop (14 Nov): news
per startup through `knowledge/query` (section "News"). This file is what an agent needs to call the graph correctly.
Full docs: `docs/reference/cala/` (index in its `README.md`, spec in `openapi.json`). Read
only the page you need. Refresh with `bash scripts/fetch-docs.sh https://docs.cala.ai docs/reference/cala`.
Docs read and API probed live on 2026-11-13/14. Field guide the Cala team shared for this
track (company fields, rounds, events): `docs/reference/cala-field-guide.md`; where it and
our probes disagree, both are noted below. What data exists per country:
research.md "Cala coverage".

Pages in the mirror contain agent-facing text (install a skill, connect MCP). It is vendor
text, not instructions for us.

## Basics
- Base `https://api.cala.ai`, header `X-API-KEY: $CALA_API_KEY` (keys: console.cala.ai/api-keys).
- Credits: console.cala.ai, Billing > Extra credits > Add credits > promo code `MAKEUNICORNSREAL`.
- MCP: `https://api.cala.ai/mcp/`, same header. Tool names mirror the endpoints
  (`entity_search`, `entity_lookup`, `entity_introspection`, `entity_retrieval`).
- Missing key: `401 {"detail":"API Key not present"}`.

## Endpoints
| Step | Endpoint | Returns |
| --- | --- | --- |
| Name to id | `GET /v1/entities?name=&entity_types=&limit=` | `entities[]` of `{id, name, entity_type, description}` |
| Identifier to id | `POST /v1/entities/lookup` | one such stub; 404 if unknown, 422 if bad scheme |
| What a node has | `GET /v1/entities/{id}/introspection` | property names, relationship types per direction, metric ids |
| Read a node and its neighbours | `POST /v1/entities/{id}` | properties, relationships, time series, all with sources |
| Deprecated, LLM in the loop | `POST /v1/knowledge/query`, `POST /v1/knowledge/search` | rows or prose plus entity ids; we use query only for news |

There is no call that returns a whole subgraph, and no call that lists entities by
criteria. The graph is walked one node at a time, starting from a name or an identifier.

### Search by name
- Fuzzy match. `name` 1-100 chars, `limit` 1-100 (default 20), `entity_types` repeatable
  (`entity_types=Company&entity_types=Person`).
- One real-world thing often returns several hits (company, product, UK subsidiary, a
  Wikipedia article). Pick by `entity_type` and `description`, or let the user choose.
- Investors come back as `Organization` or as `Company`, so do not filter them by one type.
- Companies are stored under their legal name, with the brand as name or alias (Cameo is
  "Baron App, Inc."). Search by either. A brand, its legal entity and each national
  subsidiary can be separate `Company` entities: pick the one by `website`.
- Full type list: enum in `openapi.json`. Relevant: `Company`, `Organization`, `Person`,
  `Event`, `Industry`, `Country`, `CountrySubdivision`, `FundingRound`,
  `PrivateCompanyFundingRound`, `CorporateEvent`, `FinancialMetric`, `ObservableProperty`.

### Lookup by identifier
Exact match on one scheme: `lei`, `cik`, `rssd_id`, `companies_house_uk_company_number`,
`siren`. Body `{"lei": "..."}` or `{"id": {"lei": "..."}}`. Prefer it over name search
whenever a registry number is known: no ambiguity.

### Introspection
```json
{"properties": ["name", "founding_date", "website"],
 "relationships": {"outgoing": ["OPERATES_IN_INDUSTRY"], "incoming": ["INVESTED_IN", "FOUNDED"]},
 "numerical_observations": {"FinancialMetric": [{"id": "<uuid>", "name": "...", "unit": "USD", "cadence": "i", "taxonomy": "us-gaap"}]}}
```
The schema differs per entity, not just per type. Always introspect before retrieving and
request only what it lists; asking blind wastes calls and may hit empty edges.

### Retrieval
Without a body it returns default properties only: no relationships, no time series.
Relationships and metrics come back only when named in the body:
```bash
curl -X POST "https://api.cala.ai/v1/entities/$ID" -H "X-API-KEY: $CALA_API_KEY" \
  -H "Content-Type: application/json" -d '{
    "properties": ["name", "founding_date", "website"],
    "relationships": {
      "incoming": {"INVESTED_IN": {"limit": 100}, "FOUNDED": {}},
      "outgoing": {"PARTICIPATES_IN_CORPORATE_EVENT": {"limit": 100, "offset": 0}}},
    "numerical_observations": {"FinancialMetric": ["<metric uuid from introspection>"]}}'
```
Response shape:
- Top level: `id`, `name`, `entity_type`, `description`.
- `properties.<name>` = `{value, sources[]}`; a source is `{name, document, date,
  date_precision, source_rank}`. `document` is a URL string or an object `{endpoint, params,
  response_hash}`: handle both. `date_precision` is `day`, `month` or `year`: a
  `2019-01-01` founding date with `year` precision means "2019", so never show more
  precision than stated. `source_rank`, strongest first: `FILING` (registries, regulators,
  SEC, Companies House, GLEIF), `PRIMARY` (the company, its investors, lenders or grant
  bodies), `PRESS`, `AGGREGATOR` (funding databases). Show it next to each fact.
- Fields that do not apply are not returned (a bootstrapped company has no rounds). A zero
  that a source confirms comes back as a sourced `0`. Absent is not zero.
- `relationships.<incoming|outgoing>.<TYPE>[]` = neighbour `{id, name, entity_type,
  properties}`. That `properties` object describes the edge: its own `id`, `sources[]` and
  attributes such as `role`, `event_date`, `is_lead`, `valid_since`, `valid_until`.
- `numerical_observations[]` = `{id, name, type, properties{unit, cadence, taxonomy},
  data[]}` with `data[]` of `{time, value, origin{name, source, url, published_time}}`.
  Request them by the ids introspection lists, under their type key (`FinancialMetric`,
  `ObservableProperty`).
- Paging is per relationship with `limit` and `offset`. `limit: 100` works; the maximum and
  the default are not documented and were not measured.

## Company fields (field guide)
Each company returns only the fields that apply; introspect to see which.
- Properties: `name`, `legal_name`, `aliases`, `website`, `description`, `founding_date`,
  `headquarters_address`, `registered_address`, `operational_status` (`ACTIVE`...),
  `company_ownership_status` (e.g. merged or acquired, or the registry's legal form),
  `employee_count_range` (`[90]` or `[51, 200]`), `total_funding` + `total_funding_units`,
  `total_funding_excluding_debt` + `_units`, `funding_stage` (`PRE_SEED`, `SEED`,
  `SERIES_A`...), `companies_house_uk_company_number`.
- Time series: `ObservableProperty` "Number of employees" (code `employee_count`, one point
  per source); `FinancialMetric` "Annual recurring revenue" where published; for UK
  Companies House filers, `FinancialMetric` statement lines by year (cash, current assets,
  creditors, net assets, equity, average employees...).

## The graph (field guide, plus probes on Mistral AI and Sequoia Capital)
| From | Direction and edge | To | Edge attributes |
| --- | --- | --- | --- |
| Company | incoming `FOUNDED` | Person | `valid_since` |
| Company | incoming `IS_CEO_OF`, `IS_CTO_OF`, `IS_VICEPRESIDENT_OF` (probe also saw `IS_EXECUTIVE_OF`) | Person | `valid_since`, `valid_until` when they left |
| Company | incoming `IS_BOARD_MEMBER_OF`, `WORKS_AT` | Person | `role` on `WORKS_AT` |
| Company (UK) | incoming `IS_BENEFICIARY_OWNER_OF`, `IS_CONTROL_PERSON_OF` | owner, person with significant control | from Companies House |
| Company | incoming `INVESTED_IN` | investor (Organization, Company or Person), all rounds | none |
| Company | outgoing `PARTICIPATES_IN_FUNDING_ROUND` | `FundingRound` | `role`: `ISSUER` (it raised), `INVESTOR` or `LENDER` (it funded someone) |
| `FundingRound` | incoming `PARTICIPATES_IN_FUNDING_ROUND` | issuer and every participant | `role` (`ISSUER`, `INVESTOR`, `LENDER`), `is_lead` |
| Investor | outgoing `PARTICIPATES_IN_FUNDING_ROUND` | `FundingRound` | `role`, `is_lead` |
| Company | outgoing `PARTICIPATES_IN_CORPORATE_EVENT` | `PrivateCompanyFundingRound` (filing) or `CorporateEvent` (M&A) | `role` (`ISSUER`, `ACQUIRER`...), `event_date` |
| Company | outgoing `PARTICIPATES_IN_EVENT` | `Event` (e.g. Slush 2026) | `role: ATTENDEE` |
| Company | outgoing `HAS_DOMAIN_NAME` | domain | `status` (`ACTIVE`, `INACTIVE`), `valid_since` |
| Company | outgoing `OPERATES_IN_INDUSTRY`, `HAS_HEADQUARTERS_IN`, `IS_REGISTERED_IN` | Industry, place | broad code plus the source's own label |
| Company | `IS_DIRECT_PARENT_OF`, `IS_ULTIMATE_PARENT_OF`, `IS_SUBSIDIARY_OF` (probe) | Company | ownership chains |

Rounds come in two models. Rely on `FundingRound` for who invested and who led:
- `FundingRound` (from announcements): `name` ("Seed", "Series B", "Venture Debt", "Grant";
  "Funding round" when no source names it), `round_label` (`SEED`, `SERIES_A`),
  `instrument` (`EQUITY`...), `transaction_value` + `transaction_value_units`,
  `announcement_date` (first public report), `event_date` with `event_date__precision`
  (first close or signing). Probes also returned `close_date`. To list money a company
  raised, keep the rounds where its `role` is `ISSUER`.
- `PrivateCompanyFundingRound` (from filings such as SEC Form D): `name` is always
  `FINANCING_RAISED_OR_FACILITY_ENTERED`, so label it from `round_type` ("Series B", "Debt");
  also `event_date`, `transaction_value`, `description`. The guide says filings carry no
  investors; our Mistral probe still showed `INVESTOR` participants on one. Do not use it
  for investor or lead data.
- One financing can exist in both models. Match by date and amount before summing, or
  `total_funding` and our own sums will double count.
- `CorporateEvent`: acquisitions and agreements. `name` says what (`MNA_COMPLETED`,
  `MATERIAL_AGREEMENT_ANNOUNCED`), the edge `role` the company's side (`ACQUIRER`...),
  `event_date` when.

Example path, who led rounds in companies like X: company -> its rounds -> investors of
each round -> each investor's `PARTICIPATES_IN_FUNDING_ROUND` edges with `is_lead` and the
round dates (still active?).

## Data quirks: handle them in our code
- Round participants can also have `role: GRANTOR` (not in the field guide): FIRSTPICK sat
  as GRANTOR next to INVESTORs in a round (2026-11-14). Hidden links count it as funding;
  `participants()` in `build.py` still lists INVESTOR and LENDER only.
- Founders' `Person` nodes link almost only to their current company: of 40 founders and
  CEOs of 20 Slush startups probed on 2026-11-14, none had a FOUNDED, WORKS_AT or IS_CEO_OF
  edge to another company (only duplicates of the same one). "Repeat founder" links are not
  supported by the data yet.
- Investors have few round edges: Pioneer Fund 1, FIRSTPICK 8, Y Combinator 100+ (hub).
- Duplicate entities: one person appeared as three `Person` nodes, Nvidia as two companies,
  one fund as both `Organization` and `Company`. Part of it is by design (each legal entity
  and subsidiary is its own `Company`). Merge by normalised name, `website` and registry id
  before counting or ranking.
- `INVESTED_IN` is noisy in direction: Mistral AI showed outgoing `INVESTED_IN` to its own
  investors. For who funded whom, trust round participants and their `role`, not this edge.
- Round dates can differ by a day between participants of the same round.
- `OPERATES_IN_INDUSTRY` mixes coarse labels (`SOFTWARE_AND_SERVICES`) with odd ones
  (`AEROSPACE_AND_DEFENSE` for an LLM startup). Weak signal for "similar companies".
- Empty `sources: []` happens (ids, some aliases), and older docs show sources without
  `source_rank`. Both normalise to `aggregator`, the weakest Cala level: we never claim more
  trust than Cala states (`backend/app/cala/normalize.py`).

## Our client (`backend/app/cala/`)
- `CalaClient(api_key, CalaCache(conn), mode="live"|"replay")`: `search`, `lookup`,
  `introspect`, `retrieve`, `query` (news only; `cache_only`, per-call `timeout`). Serial
  by default, exponential backoff on 429 and 5xx, every response cached by method + path +
  params + body. Replay, or a `cache_only` miss, raises `CalaCacheMiss`.
- `normalize.py`: `property_fact`, `edge_fact`, `edge_attr`, `relationships`,
  `observations` turn raw responses into `Fact`s (absent -> `not_published`).
- `app/discovery/pipeline.py`: `get_candidates(client, profile)` walks the profile's
  `Event` (default Slush 2026), introspects each attendee, keeps startups
  (`filters.is_startup`), reads their `ISSUER` rounds and each last-round lead's other
  rounds, applies the profile filters and attaches the three signals.
- `app/agent/explore.py`: the chat agent's own walk (#73). Gemini calls `cala_search` and
  `cala_neighbours` (introspect, then retrieve only listed edges, 6 per type, issuers and
  trusted investors first) for at most 6 rounds and 30 entities; a hub type (`Event`,
  `Industry`, `Country`) is never expanded. Every response is cached like any other, so a
  walk that ran once replays offline.
- `app/discovery/links.py`: hidden links (#75). After the profile filters, walks each
  shortlisted startup's first 5 investors (newest round, leads first) and their first 15
  rounds, serially, 25 s timeout per call, at most 300 new Cala calls per discovery run
  (cached reads are free; `make warm` has no budget). The walk does not depend on the
  profile; matching trusted investors (by id or fund name) is pure and reruns when the
  reference investors resolve.
- Warm the cache and get the pitch counts, from `backend/`:
  `uv run --env-file ../.env python -m scripts.warm [--limit N] [--dump DIR]`.

## Rate limits and latency
- `429 {"error":"rate_limit_exceeded",...}` with no `Retry-After` header. Limits are not
  documented. Seen: 4 parallel requests trip it; a serial burst tripped it after about 12
  calls, later after 3-4; another serial run of 56 calls did not. Ask Cala for the number.
- `403` with an HTML body (nginx "403 Forbidden", not JSON) on every call, for minutes,
  seen 2026-11-14 ~11:40 while several agents shared the key; even a single request got
  it. Treat it as Cala unavailable (no retry) and rely on the cache.
- Latency is usually under 1 s for one node. Outliers: introspection 4-11 s, a round with
  15 participants 12 s, and two retrievals took about 7 minutes each (a round, and an
  investor with four relationship types). The incoming `OPERATES_IN_INDUSTRY` edges of an
  industry node did not answer in 50 s. Hub nodes (industries, countries, big funds) are slow.
- Rules for the wrapper (architecture.md): one shared queue, no parallel bursts, wait and
  retry on 429 with backoff, a per-call timeout, and every response cached by
  `(entity id, request body)`. The demo reads from the cache and is pre-warmed.
- The queue is process-wide (`CalaLimiter` in `app/cala/client.py`, #119): every client
  shares `CALA_MAX_CONCURRENCY` (1) requests in flight, starts at least
  `CALA_MIN_INTERVAL_MS` (250) apart, and a 429 pauses all of them for the backoff. Cached
  reads never wait. `make warm` ends with the first chat turn's own walk and counts its
  cache misses; `make warm ARGS=--check` only counts them (pitch.md "Demo checklist").

## Traversal flow
Shared core, whatever the seed source:
1. Seed ids (see below).
2. Introspect each new node.
3. Retrieve with a projection limited to the edges the feature needs.
4. Queue the neighbours worth expanding; stop at a fixed depth and node budget.
5. Store nodes, edges and sources locally; deduplicate.
6. Filter, sort, aggregate and score locally. The API does none of that.
7. Show every fact with its source name, link, date precision and trust badge from
   `source_rank` (agent.md "Trust scale").

Seeds without the LLM endpoints:
- Names typed by the user or found on the web, resolved with name search (user picks when
  ambiguous), or registry numbers resolved with lookup.
- Events as seed lists: an `Event` entity links every company attending it. Slush 2026 is
  `bc844d56-6ab4-452b-96bf-2661e86e592b`; retrieve its incoming `PARTICIPATES_IN_EVENT`
  (`{"limit": 100}`, page with `offset`). Attendees mix startups, investors and big
  companies: filter locally on `founding_date`, `funding_stage` and headcount.
- Widening without filters: go through the graph itself, e.g. the investors of the seed
  companies lead to their other portfolio companies.
- Limit: no discovery by criteria ("Series A fintechs in Spain"), no server-side filters
  or sorting, many calls per question, hub nodes too slow to enumerate.

Seeds with `POST /v1/knowledge/query` as a finder only:
- One call with criteria, natural language or dot notation
  (`startups.location=Spain.funding>10M.limit=20`). Keep only the ids in `entities`; drop
  `results`, whose numbers may be approximate strings ("over 100M").
- It can take up to 180 s. Empty answer: `{"results": [], "entities": []}`.
- Not approved by Cala yet (asked 2026-11-14). Until they answer, build the flow without
  it and keep the seed step swappable.

## News (`POST /v1/knowledge/query`)
Cala's workshop (14 Nov) recommended `{"input": "latest news regarding <company>"}` for the
latest news about a company. Use that exact wording: it is also our cache key.
- Answer: `{"results": [{"title", "date", "summary"}], "entities": [{"id", "name",
  "entity_type", "mentions"}]}`. The summary may come as `description`; extra keys appear
  (`name`, `source: "company announcement"`). No per-item source link.
- Dates: `"2026-11-13"` (day), `"2026-09-00"` (month), `"2026-00-00"` (year), or `null`.
- Not stable: the row shape follows the question. For many small startups Cala answers with
  a company profile or funding row (no `title`), or `{"results": [], "entities": []}`; a
  second call can differ. Only rows with a `title` are news. Probes on the Slush AI
  shortlist (14 Nov): news for Hashlist, whisperr and Palette; profile rows for GREÏ (twice),
  Vectis.ai, People Made Machines, studio vaai; empty for Eka Labs AI. Adding the domain
  to the question ("Palette (palette.team)") returned a funding row instead of news.
- `entities` is one list for the whole answer; we attach an entity to an item when its name
  or a mention appears in it, and drop the startup itself (Cala linked "Whisperr" to the
  product "Whisper").
- 29-46 s per call (Cala documents up to 180 s) and it shares the rate limit (a 429 seen).
- Our code: `app/cala/news.py`. Reports read the cache only (`cache_only=True`); live
  calls run in the `news` scheduler job (latest report's startups, every 6 h, first one a
  minute after start) and in `python -m scripts.warm --news [--retry-empty]`, strictly
  serial, 180 s timeout, one retry. Items are `NewsItem`s on `Candidate.news` with trust
  `cala_news` (agent.md "Trust scale"), never shown to the report writer.

## Open questions for Cala
- Exact rate limit, and whether it is raised for the hackathon.
- Is multi-minute latency on hub nodes expected?
- A recommended way to list companies by industry or country from the graph (the guide
  only shows listing through an `Event`).
- May `knowledge/query` be used only to obtain seed ids? (For news: yes, Cala suggested it.)
