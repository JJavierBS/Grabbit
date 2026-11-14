# The discovery algorithm

How Grabbit walks Cala's entity graph to find and order startups, what changed on
2026-11-14/15 (#191, #192, #193, #196), why, and what was measured. Written for a reader who
has not followed the issues. Agent-facing summaries stay in `docs/agents/cala.md` and
`docs/agents/agent.md`; the dated log is `docs/agents/decisions.md`.

## Summary

| | Before | Now |
| --- | --- | --- |
| Where the walk starts | The event's attendee list, in Cala's order | The attendee list and the investors the angel trusts |
| Share of Slush it can reach | First 150 of 2,989 attendees (5 %) | All 2,989 for anything joined to a trusted investor |
| Does the angel's trust steer the search | No, it only labels the result | Yes, it decides what is read |
| One fund, many Cala entities | Matched by one entity id | Matched by id or fund name everywhere |
| Order of the shortlist | Cascade of yes/no checks | A score that is the sum of visible paths |
| Second-degree links | Sampled from each startup, shown, not ranked | Measured from the trusted side, shown and ranked |

Measured with Y Combinator and 500 Global as trusted investors (section "Results"):
startups with a trusted investor in their rounds went from 5 to 27, and candidates with any
path to a trusted investor from 5 to 45.

## The question

> Which startups at Slush are a few funding rounds away from the investors I trust?

A business angel cannot evaluate 2,989 companies. They borrow someone else's judgement: if a
fund they respect put money into a startup, somebody already did the filtering. The question
can only be answered from the funding-round graph, not from a web search, which is why it is
the one Grabbit asks of Cala.

## The graph we walk

Three node types and one edge type carry the whole algorithm:

```
Investor --PARTICIPATES_IN_FUNDING_ROUND--> FundingRound <--PARTICIPATES_IN_FUNDING_ROUND-- Company
           role INVESTOR | LENDER | GRANTOR                      role ISSUER
           is_lead
```

Cala has no reliable direct investor -> startup edge, so every step goes through the round,
which is where who paid, who led and when are recorded with their sources.

Left out on purpose:

| Not used | Why |
| --- | --- |
| `INVESTED_IN` | Its direction is wrong in some cases (Mistral AI showed it pointing at its own investors) |
| Founders and other `Person` edges | Of 40 founders and CEOs probed, none linked to a second company |
| `Industry`, `Country` nodes | Hubs: listing their neighbours takes minutes or times out |
| `knowledge/search`, `knowledge/query` for discovery | LLM-processed, lossy, being deprecated; Cala asked us to build on the entity endpoints |

Whether a company attends the event is not a graph step: it is a lookup in the attendee
list, read once (30 pages of 100) and cached.

Constraints of the API that shape everything below (`docs/agents/cala.md`):
- No call returns a subgraph or lists entities by criteria. One node per call.
- Calls are serial and rate limited (no documented limit, 429 without `Retry-After`).
- The investor -> round edge carries no date. Recency is known only after the round is read.
- One real fund is several entities: a name search for Y Combinator returns a Company, an
  Organization, a Group and vehicles such as "Y Combinator W24". The walk read 36 entities
  for Y Combinator and 500 Global together; most have no round edges.

## The previous algorithm

`backend/app/discovery/pipeline.py`, `get_candidates`:

1. Read the event's attendees and keep the first 150 (`MAX_ATTENDEES`).
2. For each: introspect, read the company, drop what is not a startup (`is_startup`).
3. Read each startup's rounds as issuer, and the participants of each round.
4. Read the last round's lead and up to 15 of its rounds (follow-on signal).
5. Hidden links (`links.py`): for each startup, its first 5 investors and 15 rounds of each,
   until 300 new Cala calls are spent.
6. Apply the profile filters and compare investors with the trusted ones by entity id.
7. Order: a trusted investor led a round, then joined one, then likely to raise, then recency.

What was wrong with it:

| Problem | Evidence |
| --- | --- |
| It saw 5 % of the event | 150 of 2,989 attendees; a perfect match at position 151 never appeared |
| The search ignored its goal | Trusted investors were only compared at the end; 76 of the 150 attendees read were not startups |
| Reading everything is not affordable | About 3 calls per attendee (456 cached calls for 150): about 9,000 serial calls for the event (estimate) |
| Fixed caps in arrival order | "5 investors, 15 rounds, 300 calls" spent the budget on whichever startups came first; 210 investors would need about 3,000 calls |
| Order was a cascade of booleans | Hidden links did not count; two startups with one and three links to trusted investors tied |
| One entity id per fund | A round listing another entity of the same fund did not match |

## The new algorithm

Discovery is now the union of two walks, followed by one scoring step:

```
            event walk (unchanged)                 reverse walk (new)
   Event -> first 150 attendees -> startups     trusted investor -> its rounds -> issuer
                     \                              |            \-> co-investors -> their rounds -> issuer
                      \                             |                         (second ring)
                       \                            v
                        +----> merge, dedupe <---- issuers that attend the event
                                    |
                     profile filters, signals, hidden links
                                    |
                          proximity score -> rank
```

With no trusted investors in the profile, only the event walk runs and behaviour is exactly
the previous one, with no extra Cala calls.

### 1. Reverse walk (#191)

`backend/app/discovery/reverse.py`, `reverse_walk`. For each trusted investor:

1. **Find every entity of the fund.** Its stored id plus Cala name-search hits whose
   normalised name is the fund's name or that name followed by more words ("Y Combinator
   W24"). A reference typed in chat (`unresolved:<name>`) resolves the same way.
2. **Read each entity's funded rounds**, paging 100 at a time, keeping the roles INVESTOR,
   LENDER and GRANTOR.
3. **Read each round once** and take its ISSUER. The request body is the event walk's own
   (`ROUND_BODY`), so both walks share cache entries.
4. **Cross issuers with the attendee list** by entity id.
5. **Attending issuers go through the event walk's own path**: company read, startup rules,
   rounds, signals. Nothing about what a candidate is has changed.

The rounds and investors it reads join the `LinkGraph`, so hidden links and the score see
them. Event-walk candidates win on a repeat (same id or same normalised name).

This is a meet-in-the-middle search: instead of expanding 2,989 attendees towards a handful
of trusted investors, it expands the handful towards the attendee list and intersects.

### 2. Second ring (#193)

Same module, `_second_ring`. After ring 1 has finished:

1. From the rounds ring 1 read, count each trusted investor's co-investors (funding roles in
   the same round, not an entity of a trusted fund) by shared rounds, merged by normalised
   name.
2. Walk the strongest like a fund entity: most shared rounds first, at most 10 per trusted
   investor, at least 2 shared rounds. No name search per co-investor (it would cost a call
   each); the entity ids seen on those rounds are used.
3. A co-investor with more than 300 round edges is a hub: skipped and logged.

This measures "friend of a friend" from the trusted side, exactly, where the previous hidden
links sampled it from each startup's side.

### 3. One fund, one identity (#196)

`backend/app/trusted.py`, `Trusted.match(entity_id, name)`: an investor is a trusted one when
the entity id matches, or the normalised names are equal, or one is the other followed by
more words and the shorter has at least two words ("500 Global" matches "500 Global (500
Emerging Europe)"; "Ugly" does not match "Ugly Duckling Ventures").

The same rule now decides the co-invest signal, the report section, the report prompt, the
onboarding count, the alert rule "led by one of your reference investors", hidden links and
the score. Before, only hidden links used it.

### 4. Proximity score (#192)

`backend/app/discovery/proximity.py`. A path joins a startup to a trusted investor:

- **Ring 1:** a trusted investor took part in one of the startup's own rounds.
- **Ring 2:** an investor of the startup shared another round with a trusted investor.

Each path has a strength, the product of these factors:

| Factor | Value | Why |
| --- | --- | --- |
| Distance | ring 1 = 1.0, ring 2 = 0.3 | Trust dilutes with every intermediary |
| Role | lead 1.0, participant 0.6 | The lead does the due diligence and sets the price |
| Recency | halves every 3 years; no date = 0.5 | A fund changes team and thesis |
| Source | filing 1.0, primary 0.9, press 0.75, aggregator 0.6; weakest edge of the path | Cala's `source_rank`: never claim more trust than the source |
| Selectivity, ring 2 only | `1 / log2(2 + rounds of the intermediary in the graph)` | Co-investing with a hub is common; co-investing with a small fund means something |

In ring 2 the role is the intermediary's role in the startup's round, and the recency is that
of the older of the two rounds.

Ring 1 counts one path per round and trusted fund: two Cala entities of one fund in the same
round ("Y Combinator" and "Y Combinator W24") are one investment, scored at the stronger one.
A trusted fund that took part as GRANTOR (FIRSTPICK) is a ring 1 path too ("gave a grant
in"), read from the raw round, since a round's investors leave grantors out (most are public
agencies). Ring 2 keeps at most 2 paths per intermediary (`MAX_PATHS_PER_INTERMEDIARY`):
its shared rounds are one piece of evidence seen several times, and without the cap a busy
intermediary filled all 5 slots and cancelled its own low selectivity.

**Score = sum of the 5 strongest paths.** Only those 5 are kept, so the number always equals
what is listed: it is never a black box. Each path carries a one-line explanation in plain
words and the sourced facts that prove it (`Candidate.proximity`).

The weights are a first calibration, named constants at the top of the module. Nothing has
been fitted to outcomes.

### 5. Ranking

`backend/app/reports/rank.py`: proximity score (higher first), then likely to raise, then
most recent round, then name. With no trusted investors the score is ignored and the order
is the previous one.

Behaviour change: a participant in a very recent round can now outrank a lead of a much
older one. The old cascade always put any lead first.

## Worked example

Trusted investor: Y Combinator. Today is November 2026.

- **Startup A.** Y Combinator led its Seed in 2026, reported by the company (primary).
  One ring 1 path: `1.0 x 1.0 x ~1.0 x 0.9 = 0.90`.
- **Startup B.** No trusted investor in its rounds. A small fund with 6 rounds in the graph
  joined its 2026 round and shared a 2025 round with Y Combinator, both from press.
  One ring 2 path: `0.3 x 0.6 x 0.79 x 0.75 x 1/log2(8) = 0.036`. Three such paths: about 0.11.
- **Startup C.** No path. Score 0.

Before: A first; B and C tied and were told apart only by round date. Now: A, then B, then
C, and B's card can say why.

## Cost and budgets

| Limit | Default | Where |
| --- | --- | --- |
| New Cala calls per reverse walk | 300 (unlimited in `make warm`) | `ReverseLimits.call_budget` |
| Timeout per call | 25 s | `ReverseLimits.timeout` |
| Name-search hits per fund | 50 | `ReverseLimits.search_limit` |
| Co-investors walked per trusted investor | 10, with at least 2 shared rounds | `co_investors`, `min_shared_rounds` |
| Hub cap | 300 round edges | `hub_round_edges` |
| Second ring switch | on | `second_ring` |
| Result cache | 15 min per (event, set of fund names) | `agent/sources.py` |

The walk never raises: over budget, on a timeout or on a Cala error it returns what it has,
and the event walk's result always comes back. A walk that spent its call budget is not kept
in the 15-minute result cache, so the next turn walks again: what it already read comes from
the Cala response cache for free (SQLite, plus Valkey when configured) and the new budget
goes further. A walk cut short by timeouts or errors only is kept, so a slow node does not
cost 25 s on every turn.

Ring 1 always completes before ring 2 starts, so a short budget costs second-degree results
first.

## Results

Method: live Cala, 2026-11-14 and 2026-11-15, Slush 2026, trusted investors Y Combinator and
500 Global, neutral profile (no stage, sector or country filter). The event walk was replayed
from the cache; the reverse walk ran live on a copy of that cache. One run, one pair of
investors.

### Coverage and yield

| KPI | Before | Ring 1 | Ring 1 + ring 2 |
| --- | --- | --- | --- |
| Candidates | 74 | 96 | 108 |
| Startups with a trusted investor in their rounds | 5 | 27 | 27 |
| Candidates with a proximity score above zero | n/a (5 by the old check) | 33 | 45 |
| New startups the event walk never saw | 0 | 22 | 34 |

### What the reverse walk read

| | Ring 1 | Ring 1 + ring 2 |
| --- | --- | --- |
| Fund entities walked | 36 | 36 |
| Co-investors walked | 0 | 11 (none over the hub cap) |
| Rounds read | 167 | 274 |
| Distinct issuers | 115 | 184 |
| Issuers attending Slush | 28 | 42 |
| Of those, startups | 27 | 40 |

One in four issuers funded by these two investors attends Slush. Y Combinator alone: 165
rounds in Cala, 100 distinct issuers in the first 150 read, 20 attending. 500 Global: 9
rounds, 6 attending.

Co-investors walked: Pioneer Fund (16 shared rounds with Y Combinator), Andreessen Horowitz
(7), Rebel Fund (6), SV Angel (6), Soma Capital (5), General Catalyst (4), Gradient Ventures
(4), Guillermo Rauch (4), Arash Ferdowsi (3), Base10 Partners (3), and FIRSTPICK (2, with 500
Global). 373 distinct co-investors were seen in total.

### Cost

| | New Cala calls |
| --- | --- |
| Reading every attendee (estimate, 3 per attendee) | about 9,000 |
| Ring 1 from a cold cache (two runs sharing a cache: 168 + 151) | about 320 |
| Ring 2 on top | 204 |

A cold cache needs about 520 calls for these two investors, more than the default budget of
300. Live, the first turn returns ring 1 partly read and later turns complete it; `make warm`
has no budget and is what the demo relies on.

### The ranking

Top of the real order (score, where the startup came from, strongest path):

| # | Score | Startup | Found by | Strongest path |
| --- | --- | --- | --- | --- |
| 1 | 1.23 | Pally | event walk | Y Combinator led its Seed (2026) |
| 2 | 1.13 | HyLight | reverse walk | Y Combinator joined its Series A (2026) |
| 3 | 0.92 | The Token Company | reverse walk | Y Combinator led its Pre-Seed (2026) |
| 4 | 0.91 | Elyos AI | reverse walk | Y Combinator joined its Series A (2026) |
| 5 | 0.85 | Nozomio | reverse walk | Y Combinator led its Pre-Seed (2025) |
| 6 | 0.83 | whisperr | event walk | 500 Global led its Pre-Seed (2026) |
| 7 | 0.78 | Userlens | reverse walk | Y Combinator in its rounds |
| 8 | 0.74 | Callsy AI | reverse walk | 500 Global in its rounds |
| 9 | 0.74 | TesterArmy | reverse walk | Y Combinator in its rounds |
| 10 | 0.74 | DAIVIN! | reverse walk | Y Combinator in its rounds |

8 of the top 10 were invisible before. Positions 1 to 26 all hold a ring 1 path; candidates
joined only through ring 2 start at position 27 with scores under 0.2, as the weights intend.

### Correctness

- The co-invest signal was filled for all 27 ring 1 startups, including those reached
  through another entity of Y Combinator.
- The startup rules dropped 2 of the 42 attending issuers.
- Backend: 501 tests pass on `main` after the merge (426 before the change). CI on `main` is
  green, frontend included.

## Limitations

| Limitation | Effect | Possible fix |
| --- | --- | --- |
| The reverse walk only finds startups joined to a trusted investor | A thesis without trusted investors still sees 150 attendees | Prioritise the event walk too, or walk it fully in `make warm` |
| Late-stage companies pass the startup rules | Helion Energy (Series G), D-ID (Series B), ElevenLabs and Modal Labs (Series D) appear with a neutral profile; a stage filter removes them | Tighten `is_startup` by stage |
| Cold cost is above the live budget | First live turn for a new pair of investors is partial | Raise the budget, or run ring 1 in the background and report progress |
| Rounds are read in Cala's order | With a short budget, old rounds may be read before recent ones | None without a date on the edge; ask Cala |
| The score outranks every other signal | Being likely to raise only breaks exact ties: a ring 2 path of 0.01 beats a likely-to-raise startup with no path | Band the score before the other keys; a product decision |
| Weights are not calibrated | The order between close scores is a judgement, not a measurement | Fit against known follow-on rounds once there is history |
| Selectivity counts rounds in the walked graph | An investor walked less looks more selective than it is | Use its total round count from Cala |
| The score is not drawn in the UI | It orders the report but the paths are only in the API | Frontend follow-up on `Candidate.proximity` |
| The chat's own walk marks trusted investors by entity id | A trusted fund under another entity is not labelled in the live walk | Pass the matcher to `agent/explore.py` |
| Cala's coverage | An investor with one round in Cala (Pioneer Fund had 1 as a seed, 16 as a co-investor) yields little | None on our side |
| One measurement | Two investors, one event, one day | Repeat with other references |

## Where it lives

| Part | Code | Tests |
| --- | --- | --- |
| Event walk | `backend/app/discovery/pipeline.py` | `tests/test_discovery.py` |
| Reverse walk and second ring | `backend/app/discovery/reverse.py` | `tests/test_discovery_reverse.py` |
| Fund identity | `backend/app/trusted.py` | `tests/test_trusted.py` |
| Hidden links | `backend/app/discovery/links.py` | `tests/test_discovery_links.py` |
| Proximity score | `backend/app/discovery/proximity.py` | `tests/test_discovery_proximity.py` |
| Ranking | `backend/app/reports/rank.py` | `tests/test_reports_rank.py` |
| Union of the walks, caching | `backend/app/agent/sources.py` | `tests/test_investor_flow.py` |
| Cache warm-up and counts | `backend/scripts/warm.py` | `tests/test_warm.py` |

## Reproduce the numbers

From `backend/`, with `CALA_API_KEY` set:

```
uv run --env-file ../.env python -m scripts.warm
```

It walks the event, then the reverse walk for Y Combinator, 500 Global and the stored
profile's investors without a budget, and prints fund entities, rounds, issuers, attending
issuers, startups reached and the second ring's counts. `--check` replays both walks from the
cache and exits 1 on any miss: run it before a demo.
