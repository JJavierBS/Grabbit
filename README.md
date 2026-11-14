# Grabbit

TODO punchline: one sentence, the same as in the submission form.

Built at Junction 2026 for the "Make Unicorns Real" challenge by Cala.

## Problem
TODO: who has it, how big it is.

## Solution
TODO: what it does, in 3-5 lines. Screenshot or GIF here.

## Demo
- Live: TODO link
- Video (2 min): TODO link

## Technologies used
TODO: keep in sync with the submission form.

## Run locally
Needs `uv`, Node 24 and npm.
```sh
make setup             # uv sync, npm ci, hooks; creates .env from .env.example
make dev               # API on :8000, web app on http://localhost:5173
```
Offline (no keys): set `CALA_MODE=replay` and `LLM_MODE=fake` in `.env`.

| Command | What it does |
| --- | --- |
| `make test` | Backend pytest and frontend Vitest, quiet |
| `make lint` | ruff, Biome and the TypeScript check |
| `make fmt` | Formats only the files changed on your branch |
| `make gen-api` | Regenerates `frontend/src/api/schema.ts` from the running API |
| `make warm` | Fills the Cala cache for the demo (`ARGS="--limit 150"` to sample) |
| `make docker` | Builds the production image (frontend served by FastAPI on :8000) |

API docs while `make dev` runs: http://localhost:8000/api/docs

## Deploy
The demo runs on an AWS Lightsail container service (one container, port 8000, HTTPS
endpoint from Lightsail). One-time: install the aws CLI v2 and the `lightsailctl` plugin,
and run `aws configure` with an IAM user allowed to use Lightsail. Then:
```sh
make warm      # fill data/grabbit.db so the image ships the Cala cache
make deploy    # builds the image, pushes it and deploys; prints the public URL
```
Secrets (`GEMINI_API_KEY`, `GEMINI_MODEL`, `CALA_API_KEY`, `CONTEXT_DEV_API_KEY`) are read
from `.env` and set as service environment variables, never baked into the image. The
deployed app runs with `CALA_MODE=replay` and `DEMO_MODE=1`; override with
`DEPLOY_CALA_MODE=live make deploy`. Other knobs: `LIGHTSAIL_SERVICE` (default `grabbit`),
`LIGHTSAIL_POWER` (default `micro`), `AWS_REGION` (default `eu-north-1`).

## Contributing
After cloning, run `bash scripts/setup.sh` once (hooks, local exclusions, `.env`).
Then follow `AGENTS.md`: one issue, one branch, one PR; never push to `main`.
Raw briefs and partner docs live in `docs/reference/`; refresh a docs mirror with
`bash scripts/fetch-docs.sh [base_url] [dest]` (default: Context.dev).
How we manage issues, the board, labels and milestones: `docs/agents/workflow.md`.

Commit messages and PR titles: `[<github-user>] [<TYPE>] (#<issue>) <Summary>`, e.g.
`[JJavierBS] [FEATURE] (#12) Add Cala API wrapper`. TYPE is FEATURE, FIX, DOCS, CHORE...
Leave out `(#<issue>)` only when there is no issue. Details in `docs/agents/commits.md`.

**Important: no AI attribution anywhere.** Commits, PR titles and descriptions, branch
names, issues and code comments must not mention AI tools: no `Co-Authored-By` trailers
for assistants, no "Generated with ...". The `commit-msg` hook rejects them; configure
your assistant so it does not add them.

## Team
- Francisco Moreno Sanchez: TODO role
- José Javier Bravo Sarabia: TODO role
- Juan López Bravo: TODO role
- Rubén Moyano Palazón: TODO role

## License
MIT, see [LICENSE](LICENSE). Partner APIs and data are subject to their own terms.
