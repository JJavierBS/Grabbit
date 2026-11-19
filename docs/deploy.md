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
run out. You need `make setup` done and the Valkey URI from the Aiven console
(`grabbit-cache` > Overview > Service URI, it starts with `rediss://`):
```sh
git pull && cd backend
VALKEY_URL='rediss://...' uv run python -m scripts.export_valkey ../data/grabbit.db ../data/grabbit-demo.db --strip
DATABASE_PATH=data/grabbit-demo.db CALA_MODE=replay make -C .. warm ARGS=--check
```
- The source is your `data/grabbit.db` from the event; it is only copied, never modified.
  Without one, ask a teammate for theirs: the cache itself comes from Valkey.
- The export prints how many keys it read: the full export of November 2026 read 2,809 keys
  (a laptop copy had 941 rows) and weighs 14.5 MB, with 0 misses on both checks (#242). `--strip` empties chats, profiles, reports, alerts and snapshots.
- The check should print `0 cache misses` on both lines. A few misses on the reverse walk
  still make a useful snapshot: publish it and note the numbers in the tracking issue.
- Both files stay in `data/`, which git ignores: never commit the snapshot, Cala's data stays
  under Cala's terms. Publish it as a release asset instead (step 3 of "Go live").

## Go live on grabbit.cloud
Everything left needs an account, so each step says who can do it. In order:
1. **Save the Cala cache** (anyone with the Aiven console): "Demo snapshot" above. Urgent:
   Aiven powers Valkey off when the trial credits run out, and the trust walk cannot be
   rebuilt without Cala.
2. **Ask Cala** whether the snapshot may be public (whoever keeps the Cala contact), e.g.
   *"After Junction we keep Grabbit online as a portfolio demo. It no longer calls your API:
   it answers from a snapshot of the responses we cached during the event (about 15 MB,
   November 2026), published as a GitHub release asset. Is that OK with you, or would you
   rather we keep it private?"* If they say no, skip step 3 and deploy without
   `DEMO_DB_URL`: the agent then runs on the fixture candidates.
3. **Publish the snapshot** (anyone with write access to the repo, from the repo root):
   ```sh
   gh release create demo-snapshot-2026-11 data/grabbit-demo.db \
     --title "Demo snapshot: Cala cache, November 2026" \
     --notes "SQLite cache of Cala responses from Junction 2026, for CALA_MODE=replay. Cala's data, under Cala's terms."
   ```
   Its URL is `https://github.com/JJavierBS/Grabbit/releases/download/demo-snapshot-2026-11/grabbit-demo.db`.
4. **Create the Render service** (whoever will own the demo): the Deploy to Render button in
   the README, or Render > New > Blueprint on this repo. Fill `DEMO_DB_URL` with the URL
   above and, optionally, `GEMINI_API_KEY` and `OPENAI_COMPAT_API_KEY`. The first build takes
   a few minutes; then `https://<service>.onrender.com/api/health` answers `"status":"ok"`.
5. **Point the domain** (Render owner, then whoever has the IONOS account): "Custom domain"
   above.
6. **Retire the old hosting**: in Vercel (project owner) remove both domains and disconnect
   the repository, then delete `frontend/vercel.json` in a PR; Aiven powers itself off, or
   delete `grabbit-app` and `grabbit-cache` once step 1 is done.
7. **Keep it awake** (optional, a repo admin): GitHub > Settings > Secrets and variables >
   Actions > Variables: `KEEPALIVE_URL` = `https://www.grabbit.cloud`.
8. **Check it** (anyone): open https://www.grabbit.cloud and walk the five steps of the
   README's "Try it". Expect "Scripted demo" in the top bar if no AI key was set.

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

