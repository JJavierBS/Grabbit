# Cala fixtures

Response bodies in Cala's shape, used by tests through respx or by building candidates
directly. No network in tests.

Two kinds:
- Hand-written (`company_startup.json`, `round_seed.json`): invented names, built from
  `docs/agents/cala.md` and `docs/reference/cala-field-guide.md` to cover every case
  (every `source_rank`, both `document` shapes, executives, headcount series). Most tests
  assert on their values, so keep them.
- Recorded (`real_*.json`): real responses from the Slush 2026 warm-up on 2026-11-14,
  unedited. `test_cala_real.py` checks our parsing against them. Record more with
  `python -m scripts.warm --limit N --dump <dir>` (one file per node).

| File | What it is |
| --- | --- |
| `company_startup.json` | Hand-written startup: every `source_rank`, both `document` shapes, a year-precision date, rounds, executives, headcount series |
| `round_seed.json` | Hand-written `FundingRound` with its issuer and participants, one lead |
| `real_company_rupert.json` | Recorded Slush attendee (seed startup): no founding date, no headcount series |
| `real_round_rupert_seed.json` | Recorded seed round: no `event_date` (only `announcement_date`), two leads, `is_lead` absent on the others |
| `real_news_hashlist.json` | Recorded `POST /v1/knowledge/query` "latest news regarding Hashlist": summaries under `description`, one undated item, mentioned products |
| `real_news_whisperr.json` | Same for whisperr: summaries under `summary`, Cala links the mention "Whisperr" to the product "Whisper" |

What the recordings taught us (2026-11-14): rounds may lack `event_date`; most startups
have no `employee_count` series, so `likely_to_raise` is often null; Cala answered 429
after a few dozen fast calls and the backoff recovered.
