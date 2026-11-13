#!/usr/bin/env bash
# Move an issue on the project board: scripts/board.sh <issue-number> "<Status>"
# Status: Backlog | Ready | In progress | In review | Done
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: scripts/board.sh <issue-number> \"<Status>\"" >&2; exit 2; }
num="$1" status="$2"
conf="$(git rev-parse --show-toplevel)/.github/project.env"
[ -f "$conf" ] || { echo "board.sh: $conf missing; the board is not set up yet, ask the repo owner." >&2; exit 1; }
# shellcheck disable=SC1090
. "$conf"

url="$(gh issue view "$num" --json url --jq .url)"
project_id="$(gh project view "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --format json --jq .id)"
item="$(gh project item-list "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --limit 1000 --format json \
  --jq ".items[] | select(.content.url == \"$url\") | .id")"
[ -n "$item" ] || item="$(gh project item-add "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --url "$url" --format json --jq .id)"

field="$(gh project field-list "$PROJECT_NUMBER" --owner "$PROJECT_OWNER" --format json \
  --jq '.fields[] | select(.name == "Status")')"
field_id="$(jq -r .id <<<"$field")"
option_id="$(jq -r --arg s "$status" '.options[] | select(.name == $s) | .id' <<<"$field")"
[ -n "$option_id" ] || { echo "board.sh: unknown status '$status'. Options: $(jq -r '[.options[].name] | join(", ")' <<<"$field")" >&2; exit 1; }

gh project item-edit --id "$item" --project-id "$project_id" --field-id "$field_id" \
  --single-select-option-id "$option_id" >/dev/null
echo "#$num -> $status"
