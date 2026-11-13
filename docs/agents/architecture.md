# Architecture

Keep this file under 80 lines. Update it in the PR that adds or moves a module.

## Overview
TODO: 3-5 lines. What runs where, how a request flows end to end.

## Components
| Component | Path | Owner | Purpose |
| --- | --- | --- | --- |
| TODO | | | |

## Data
- Storage: TODO
- Main entities: TODO (name: key fields)

## External services
| Service | Used for | Env vars |
| --- | --- | --- |
| Cala API / MCP (`https://api.cala.ai`) | Companies, people, funding rounds, investors | `CALA_API_KEY` |

## Directory layout
TODO: only top two levels, one line each.

## Constraints
- Demo must run from a clean clone with `make setup && make dev`.
- Demo runs from our own laptop on crowded venue wifi: the core flow must work locally, with
  cached or recorded responses as fallback for slow external APIs.
- A deployed demo link is required in the submission.
- Cala must be core to the product, not an add-on (25% of the partner score).
- All Cala calls go through one wrapper with timeout and a response cache.
