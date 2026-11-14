#!/usr/bin/env bash
# One-time setup of the EC2 host for the deploy workflow: make server-init
# Uploads the app secrets and the warmed SQLite cache and installs the deploy key: the
# public key in DEPLOY_PUBKEY when the repo owner made the pair, otherwise a new pair here
# and the GitHub settings to set. Safe to rerun: it never overwrites the
# server's .env or database unless SYNC_ENV=1 or SYNC_DB=1.
# Needs in the environment or .env: DEPLOY_HOST, SSH_KEY (the AWS .pem for this host).
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env
  set +a
fi
: "${DEPLOY_HOST:?set DEPLOY_HOST in .env (the EC2 public IP or name)}"
: "${SSH_KEY:?set SSH_KEY in .env (path to the AWS .pem for that host)}"
user="${DEPLOY_USER:-ubuntu}"
target="$user@$DEPLOY_HOST"
remote_root=/opt/junction
deploy_key="${DEPLOY_KEY:-$HOME/.ssh/grabbit_deploy}"
ssh_cmd=(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new "$target")
scp_cmd=(scp -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new)

"${ssh_cmd[@]}" "sudo mkdir -p $remote_root/data $remote_root/deploy &&
  sudo chown $user:$user $remote_root $remote_root/deploy"
"${scp_cmd[@]}" deploy/Caddyfile deploy/rollout.sh "$target:$remote_root/deploy/"

missing() { ! "${ssh_cmd[@]}" "test -e $1"; }

if [ "${SYNC_ENV:-0}" = 1 ] || missing "$remote_root/.env"; then
  [ -f .env ] || { echo "server-init: no local .env to upload" >&2; exit 1; }
  env_file="$(mktemp)"
  trap 'rm -f "$env_file"' EXIT
  # docker --env-file keeps inline comments as part of the value, so strip them here.
  grep -E '^[A-Z_][A-Z0-9_]*=' .env |
    sed -E 's/[[:space:]]+#.*$//' |
    grep -vE '^(DATABASE_PATH|DEPLOY_[A-Z_]*|SSH_KEY|CALA_MODE|DEMO_MODE)=' > "$env_file" || true
  printf 'CALA_MODE=%s\nDEMO_MODE=1\n' "${DEPLOY_CALA_MODE:-replay}" >> "$env_file"
  chmod 600 "$env_file"
  "${scp_cmd[@]}" "$env_file" "$target:$remote_root/.env"
  "${ssh_cmd[@]}" "chmod 600 $remote_root/.env"
  echo "Uploaded $remote_root/.env ($(wc -l < "$env_file") variables)"
fi

if [ -f data/grabbit.db ] && { [ "${SYNC_DB:-0}" = 1 ] || missing "$remote_root/data/grabbit.db"; }; then
  python3 -c "import sqlite3; sqlite3.connect('data/grabbit.db').execute('PRAGMA wal_checkpoint(TRUNCATE)')"
  "${scp_cmd[@]}" data/grabbit.db "$target:/tmp/grabbit.db"
  "${ssh_cmd[@]}" "sudo rm -f $remote_root/data/grabbit.db-wal $remote_root/data/grabbit.db-shm &&
    sudo mv /tmp/grabbit.db $remote_root/data/grabbit.db"
  echo "Uploaded the warmed cache to $remote_root/data/grabbit.db"
fi
# The image runs as uid 1001 (Dockerfile), which must own the SQLite files.
"${ssh_cmd[@]}" "sudo chown -R 1001:1001 $remote_root/data"

# A dedicated key for GitHub, so the AWS .pem never leaves this laptop and can stay valid
# if the deploy key is revoked.
pub="${DEPLOY_PUBKEY:-}"
if [ -z "$pub" ]; then
  [ -f "$deploy_key" ] || ssh-keygen -q -t ed25519 -N '' -C grabbit-deploy -f "$deploy_key"
  pub="$(cat "$deploy_key.pub")"
fi
case "$pub" in
  ssh-ed25519\ * | ssh-rsa\ * | ecdsa-sha2-*) ;;
  *) echo "server-init: DEPLOY_PUBKEY is not an SSH public key" >&2; exit 1 ;;
esac
# shellcheck disable=SC2016 # $key expands on the server
printf '%s\n' "$pub" | "${ssh_cmd[@]}" 'touch ~/.ssh/authorized_keys && read -r key &&
  { grep -qxF "$key" ~/.ssh/authorized_keys || printf "%s\n" "$key" >> ~/.ssh/authorized_keys; }'
echo "Deploy key installed: ${pub##* }"

if [ -n "${DEPLOY_PUBKEY:-}" ]; then
  echo "Server ready. Deploy with: make deploy"
  exit 0
fi
cat <<EOF

Server ready. The repo owner (secrets need admin) sets, once:
  gh secret set DEPLOY_SSH_KEY < $deploy_key
  ssh-keyscan -t ed25519 $DEPLOY_HOST 2>/dev/null | gh secret set DEPLOY_KNOWN_HOSTS
  gh variable set DEPLOY_HOST --body $DEPLOY_HOST
  gh variable set DEPLOY_USER --body $user
Then deploy with: make deploy
EOF
