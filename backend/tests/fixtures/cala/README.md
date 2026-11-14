# Cala fixtures

Response bodies in Cala's shape, used by tests through respx or by building candidates
directly. No network in tests.

Until real recordings land, these are hand-written from the shapes in
`docs/agents/cala.md` and `docs/reference/cala-field-guide.md` (entity names are invented).
Replace them with trimmed real responses from `backend/scripts/record_fixtures.py`
(TODO(#23)), keeping the file names so tests keep working.

| File | What it is |
| --- | --- |
| `company_startup.json` | Retrieval of a startup: properties with every `source_rank`, both `document` shapes, a year-precision date, rounds, executives, headcount series |
| `round_seed.json` | A `FundingRound` with its issuer and participants, one lead |
