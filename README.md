# Grabbit

Slush has 2,989 attendees and you are one person. Grabbit finds the startups backed by the investors you trust, shows the source of every fact, and alerts you when one of them moves.

Built at Junction 2026 for the "Make Unicorns Real" challenge by Cala.

## Problem
Slush 2026 has 2,989 attendees in Cala's graph. A business angel has one calendar and no
analyst. The angel opens tab after tab, reads databases that are months old, and arrives
tired at the only part that matters: the decision. The same pain reaches every investor who
decides alone and cannot build a research system: search funds, small private equity,
individual investors.

Two investor interviews (pseudonymised) shaped the product. One said: "I have no time to
scout; if a tool pre-selects and I review each pick by hand, I've already won." Findings:
[docs/agents/research.md](docs/agents/research.md).

## Solution
Grabbit is a proactive agent, not a dashboard.
1. **You give a vague thesis.** "AI, pre-seed or seed, backed by people I trust."
2. **It asks before it answers.** Two or three questions, each with numbers from Cala.
3. **You get a Slush shortlist.** Who led each round and which of your trusted investors
   joined it. Each fact shows a trust badge from Cala's `source_rank`: Official filing,
   Company or investor, Press, Database. An absent field reads "Not published", never zero.
4. **You correct it in plain words.** "Shorter, co-investors first." The agent rewrites its
   own instructions and the report changes on screen. A history shows what it learned.
5. **You leave. It watches.** A desktop notification tells you what changed on your
   shortlist and why it matters.

Grabbit never tells you what to buy. The alert in the demo is a simulated event, labelled
on screen; it goes through the real diff, importance check and delivery path.

TODO: screenshot or GIF here.

## Demo
- Live: TODO link
- Video (2 min): TODO link

## Technologies used
Cala entity API, Gemini (`google-genai`), Context.dev, FastAPI (Python, uv), React and
TypeScript (Vite), OpenUI (`@openuidev/react-lang`, generative UI in chat answers), SQLite,
APScheduler, Server-Sent Events, Docker on AWS EC2 behind Caddy, deployed by GitHub Actions.

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
The demo runs on one AWS EC2 host: a Caddy edge on port 80 proxies to one app container,
and each deploy starts the new image next to the old one (blue/green), moves traffic only
once it is healthy, then stops the old one. No downtime; a broken image never goes live.
`.github/workflows/deploy.yml` runs on every push to `main`: `make test lint`, image to
GHCR, then `deploy/rollout.sh` on the host over SSH. PRs run only the tests.

One-time setup (needs `DEPLOY_HOST` and `SSH_KEY`, the AWS `.pem`, in `.env`):
```sh
make warm          # fill data/grabbit.db so the server starts with the Cala cache
make server-init   # uploads the server .env and the cache, installs a deploy key
```
`server-init` prints the `gh secret set` / `gh variable set` commands for
`DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`, `DEPLOY_HOST` and `DEPLOY_USER`; repo secrets need
the repo owner. The security group must allow inbound TCP 80. Until `DEPLOY_HOST` is set
the workflow builds the image and skips the deploy.

App secrets live only in `/opt/junction/.env` on the host (`server-init` writes it once
from your `.env`, with `CALA_MODE=replay` unless `DEPLOY_CALA_MODE` says otherwise, and
`DEMO_MODE=1`); edit it there and redeploy to change them. SQLite lives in
`/opt/junction/data` and survives deploys; `SYNC_DB=1 make server-init` replaces it.
`make deploy` reruns the workflow on `main`. HTTP only for now: set `SITE_ADDRESS` to a
domain pointed at the host in the server `.env`, open port 443 and remove the
`grabbit-edge` container once, and the next deploy restarts it with automatic HTTPS.

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
