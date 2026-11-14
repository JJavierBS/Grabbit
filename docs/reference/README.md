# Reference material

Raw sources, versioned so every teammate and agent has them on clone. Agents start from the
distilled summaries in `docs/agents/` and open a page here only when they need the detail.
Do not edit mirrors by hand: regenerate them with `scripts/fetch-docs.sh`.

| Path | What | Source | Summary |
| --- | --- | --- | --- |
| `cala-track-brief.md` | "Make Unicorns Real" challenge page, verbatim | hackjunction.app/participate/45/challenges/350 | `docs/agents/challenge.md` |
| `cala-field-guide.md` | Company and funding field guide, verbatim | Shared by the Cala team, 2026-11-14 | `docs/agents/cala.md` |
| `context-dev-hackerpack.md` | Context.dev hackerpack page, verbatim | hackjunction.app/participate/45/hackerpacks/60 | `docs/agents/context-dev.md` |
| `context-dev/` | Full Context.dev docs (210 pages + `openapi.json`) | `bash scripts/fetch-docs.sh` from docs.context.dev | `docs/agents/context-dev.md` |
| `cala/` | Full Cala docs (17 pages + `openapi.json`) | `bash scripts/fetch-docs.sh https://docs.cala.ai docs/reference/cala` | `docs/agents/cala.md` |
