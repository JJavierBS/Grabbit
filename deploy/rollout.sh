#!/usr/bin/env bash
# Blue/green rollout of one Grabbit image on the EC2 host: deploy/rollout.sh <image>
# The new container must be healthy before Caddy sends it traffic; on any failure the
# running container keeps serving. Runs on the server (the deploy workflow calls it).
set -euo pipefail

image="${1:?usage: rollout.sh <image>}"
root="${GRABBIT_ROOT:-/opt/junction}"
here="$(cd "$(dirname "$0")" && pwd)"
network="${GRABBIT_NETWORK:-grabbit}"
edge="grabbit-edge"
edge_image="${EDGE_IMAGE:-caddy:2.10-alpine}"
health_timeout="${HEALTH_TIMEOUT:-90}"
poll="${POLL_INTERVAL:-2}"
edge_url="${EDGE_HEALTH_URL:-http://localhost/api/health}"

log() { echo "rollout: $*" >&2; }

mkdir -p "$root/edge" "$root/data" "$root/caddy"
exec 9>"$root/.rollout.lock"
flock -n 9 || { log "another rollout is running"; exit 1; }

active="$(cat "$root/active" 2>/dev/null || true)"
case "$active" in
  blue) next=green ;;
  *) next=blue ;;
esac
upstream="$root/edge/upstream.caddy"

write_upstream() { echo "reverse_proxy grabbit-$1:8000" > "$upstream"; }
reload_edge() {
  docker exec "$edge" caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile >/dev/null
}
health() {
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$1" \
    2>/dev/null || echo missing
}
discard_next() {
  docker logs --tail 50 "grabbit-$next" >&2 || true
  docker rm -f "grabbit-$next" >/dev/null 2>&1 || true
}

docker network inspect "$network" >/dev/null 2>&1 || docker network create "$network" >/dev/null
cp "$here/Caddyfile" "$root/edge/Caddyfile"
[ -f "$upstream" ] || write_upstream "${active:-$next}"
if [ "$(docker inspect -f '{{.State.Running}}' "$edge" 2>/dev/null || true)" != "true" ]; then
  log "starting $edge"
  docker rm -f "$edge" >/dev/null 2>&1 || true
  docker pull -q "$edge_image" >/dev/null
  site="$(sed -n 's/^SITE_ADDRESS=\([^[:space:]#]*\).*/\1/p' "$root/.env" 2>/dev/null | tail -1)"
  docker run -d --name "$edge" --network "$network" --restart unless-stopped \
    -p 80:80 -p 443:443 -e "SITE_ADDRESS=${site:-:80}" \
    -v "$root/edge:/etc/caddy:ro" -v "$root/caddy:/data" "$edge_image" >/dev/null
fi

log "deploying $image as grabbit-$next (active: ${active:-none})"
[ "${SKIP_PULL:-0}" = 1 ] || docker pull -q "$image" >/dev/null
docker rm -f "grabbit-$next" >/dev/null 2>&1 || true
# -e after --env-file wins, so a stray DATABASE_PATH in .env cannot move the database.
docker run -d --name "grabbit-$next" --network "$network" --restart unless-stopped \
  --env-file "$root/.env" -e DATABASE_PATH=/app/data/grabbit.db \
  -v "$root/data:/app/data" "$image" >/dev/null

waited=0
until [ "$(health "grabbit-$next")" = healthy ]; do
  status="$(health "grabbit-$next")"
  if [ "$status" = unhealthy ] || [ "$status" = missing ] || [ "$waited" -ge "$health_timeout" ]; then
    log "grabbit-$next is $status after ${waited}s; keeping ${active:-nothing} live"
    discard_next
    exit 1
  fi
  sleep "$poll"
  waited=$((waited + poll))
done

write_upstream "$next"
reload_edge
if ! curl -fsS --retry 5 --retry-delay 1 --retry-all-errors -o /dev/null "$edge_url"; then
  log "edge check failed through $edge_url; rolling back"
  if [ -n "$active" ]; then
    write_upstream "$active"
    reload_edge || true
  fi
  discard_next
  exit 1
fi

echo "$next" > "$root/active"
if [ -n "$active" ] && [ "$active" != "$next" ]; then
  # Grace period so in-flight requests finish; SSE clients reconnect through the edge.
  docker stop -t 30 "grabbit-$active" >/dev/null 2>&1 || true
  docker rm "grabbit-$active" >/dev/null 2>&1 || true
fi
docker image prune -af >/dev/null 2>&1 || true
log "grabbit-$next is live"
