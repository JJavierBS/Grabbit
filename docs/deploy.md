# Deploy

How the demo is hosted and how to redeploy it. The README keeps only the links.

The demo runs at https://www.grabbit.cloud, free, on one Render web service that builds the
root `Dockerfile` and serves the web app and the API from one process. It answers from a
snapshot of the Cala cache (`CALA_MODE=replay`) and from whatever free AI has a key
(`LLM_MODE=auto`: Gemini, then Groq, then the scripted demo). IONOS holds the domain and its DNS.

## Deploy your own copy (free)
1. Fork the repository. In Render: **New > Blueprint**, pick the fork. `render.yaml` creates
   the `grabbit` web service on the free plan and asks for:
   - `DEMO_DB_URL`: the demo snapshot's release asset URL (#231). Empty: the app runs on
     the fixture candidates.
   - `GEMINI_API_KEY` (aistudio.google.com) and `OPENAI_COMPAT_API_KEY`
     (console.groq.com/keys): optional and free. With neither, the agent follows the demo
     script and the top bar says "Scripted demo".
2. Every push to the fork's `main` redeploys. `/api/health` lists the AI that answers.
3. The free plan sleeps after 15 min without traffic and takes about a minute to wake. To
   keep it awake, set the repository variable `KEEPALIVE_URL` to the service URL:
   `.github/workflows/keepalive.yml` pings it every 14 min (~720 of the 750 free hours a
   month). GitHub pauses scheduled workflows after 60 days without commits.
4. SQLite is not persistent on the free plan: a restart or redeploy empties profiles, chats
   and reports, and the snapshot comes back with the image.

## Custom domain
For grabbit.cloud (or yours), once the service is live:
1. Render > `grabbit` > Settings > **Custom Domains**: add `grabbit.cloud` and
   `www.grabbit.cloud`. Render shows the records to create.
2. In the DNS provider (IONOS > Domains > grabbit.cloud > DNS): `@` **A** to the IP Render
   shows, `www` **CNAME** to the service's `*.onrender.com` host. Delete the old records
   (Vercel's `A 76.76.21.21` and `CNAME cname.vercel-dns.com`) and any **AAAA** record,
   which keeps Render from verifying the domain.
3. Render verifies the domain and issues the certificate. Then remove the domain from the
   Vercel project and disconnect it, so pushes to `main` stop building there.

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

## Legacy: Vercel and Aiven
The hosting during and right after Junction, paid from Aiven's 50 USD trial credits.
- Frontend on Vercel: the project's root directory is `frontend/`, built with
  `frontend/vercel.json`, which proxies `/api/*` (REST and the SSE stream) to the Aiven host.
- `grabbit-app` (Aiven Runtime, `startup-100-2048`, project `grabbit`, AWS `eu-central-1`,
  https://cosmic-enhanced-jawfish.eur-1.aiven.app) served the API from the root
  `Dockerfile`, deployed by hand from the console.
- `grabbit-cache` (Aiven for Valkey, Hobbyist) held the shared Cala cache, injected as
  `VALKEY_URL`. Export it before it powers off (#231).
- With no card on file, Aiven powers both off when the credits run out instead of charging.

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

