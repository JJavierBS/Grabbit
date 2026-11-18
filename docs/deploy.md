# Deploy

How the demo is hosted and how to redeploy it. The README keeps only the links.

The demo runs at https://www.grabbit.cloud; `grabbit.cloud` redirects there. IONOS holds the
domain and its DNS.
- Frontend on Vercel: the project's root directory is `frontend/`, built with
  `frontend/vercel.json`. Every push to `main` deploys to production; PRs get preview links.
  Vercel issues the certificates for `grabbit.cloud` and `www.grabbit.cloud` and does the
  apex redirect. `frontend/vercel.json` proxies `/api/*` (REST and the SSE stream) to the
  Aiven host, so the browser stays on one origin and the API needs no CORS.
- `grabbit-app` (Aiven Runtime, `startup-100-2048`, project `grabbit`, AWS `eu-central-1`,
  https://cosmic-enhanced-jawfish.eur-1.aiven.app) serves the API: it builds the root
  `Dockerfile` from `main` on port 8000. Merging does **not** deploy it: use
  Runtime > `grabbit-app` > Actions > **Deploy latest commit** in the console. Keys and
  modes are its environment variables (keys as secrets); `CALA_MODE=replay`. If the
  Aiven host changes, update the `/api` rewrite in `frontend/vercel.json`.
- `grabbit-cache` (Aiven for Valkey, Hobbyist) holds the shared Cala cache; Aiven injects its
  URI into the app as `VALKEY_URL`. Fill it from your laptop with `VALKEY_URL` in `.env`
  and `make warm` (plus `ARGS="--news"`); the app sees new entries without a redeploy.
- SQLite in the app is not persistent: every deploy starts with empty profiles, chats and
  reports. The Cala cache survives because it lives in Valkey.
- Both are paid from Aiven's 50 USD trial credits; with no card on file, Aiven powers them
  off when the credits run out instead of charging.

## Demo snapshot of the Cala cache
Cala is no longer called after the event, so every demo answers from a snapshot of the cache
(`CALA_MODE=replay`). The full cache lives in Aiven Valkey; save it before the Aiven credits
run out. With the Valkey URI from the Aiven console (`grabbit-cache` > Overview):
```sh
cd backend
VALKEY_URL='rediss://...' uv run python -m scripts.export_valkey ../data/grabbit.db ../grabbit-demo.db --strip
DATABASE_PATH=grabbit-demo.db CALA_MODE=replay make -C .. warm ARGS=--check   # 0 misses expected
```
The source file is never modified; `--strip` empties chats, profiles, reports, alerts and
snapshots so the file can be shared. Upload `grabbit-demo.db` as an asset of a GitHub
release (`demo-snapshot-2026-11`), not into git: Cala's data stays under Cala's terms.

## Legacy: AWS EC2
The first deploy, no longer the demo link. It runs on one AWS EC2 host: a Caddy edge on port 80 proxies to one app container,
and each deploy starts the new image next to the old one (blue/green), moves traffic only
once it is healthy, then stops the old one. No downtime; a broken image never goes live.
`.github/workflows/deploy.yml` runs on every push to `main`: `make test lint`, image to
GHCR, then `deploy/rollout.sh` on the host over SSH. PRs run only the tests.

One-time setup (needs `DEPLOY_HOST` and `SSH_KEY`, the AWS `.pem`, in `.env`):
```sh
make warm          # fill data/grabbit.db so the server starts with the Cala cache
make server-init   # uploads the server .env and the cache, installs a deploy key
```
The workflow needs secrets `DEPLOY_SSH_KEY` and `DEPLOY_KNOWN_HOSTS` and variables
`DEPLOY_HOST` and `DEPLOY_USER`; repo secrets need the repo owner. Either the owner makes
the key pair, sets them and you pass the public key as `DEPLOY_PUBKEY='ssh-ed25519 ...'`,
or `server-init` makes the pair and prints the `gh secret set` commands to run. The security group must allow inbound TCP 80. Until `DEPLOY_HOST` is set
the workflow builds the image and skips the deploy.

App secrets live only in `/opt/junction/.env` on the host (`server-init` writes it once
from your `.env`, with `CALA_MODE=replay` unless `DEPLOY_CALA_MODE` says otherwise, and
`DEMO_MODE=1`); edit it there and redeploy to change them. SQLite lives in
`/opt/junction/data` and survives deploys; `SYNC_DB=1 make server-init` replaces it.
`make deploy` reruns the workflow on `main`. HTTP only for now: set `SITE_ADDRESS` to a
domain pointed at the host in the server `.env`, open port 443 and remove the
`grabbit-edge` container once, and the next deploy restarts it with automatic HTTPS.

