#!/usr/bin/env bash
# Every team member runs this once after cloning: bash scripts/setup.sh
# Idempotent. Installs hooks, local exclusions and checks the toolchain.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
cd "$root"

current="$(git config --get core.hooksPath || true)"
if [ -n "$current" ] && [ "$current" != "scripts/hooks" ]; then
  echo "WARN: core.hooksPath was '$current'; replacing with scripts/hooks."
fi
git config core.hooksPath scripts/hooks
chmod +x scripts/hooks/pre-commit scripts/hooks/commit-msg scripts/hooks/pre-push scripts/board.sh
echo "Hooks: scripts/hooks"

# Personal files stay out of git without listing them in the shared .gitignore.
exclude="$(git rev-parse --git-path info/exclude)"
mkdir -p "$(dirname "$exclude")"
touch "$exclude"
tmp="$(mktemp)"
sed '/^# >>> team-local$/,/^# <<< team-local$/d' "$exclude" > "$tmp"
{
  cat "$tmp"
  echo '# >>> team-local'
  printf '%s\n' /material/ /CLAUDE.local.md /AGENTS.local.md /.claude/settings.local.json /.claude/worktrees/
  echo '# <<< team-local'
} > "$exclude"
rm -f "$tmp"
echo "Local exclusions: $exclude"

mkdir -p material
[ -f material/README.md ] || printf '# material\nRaw briefs, slides and datasets. Local only; summarise into docs/agents/challenge.md.\n' > material/README.md
[ -f CLAUDE.local.md ] || printf '# Personal notes for my agents (not versioned)\n' > CLAUDE.local.md
[ -f .env ] || { [ -f .env.example ] && cp .env.example .env && echo "Created .env from .env.example: fill it in."; }

echo "--- Checks ---"
# Personal global ignores (e.g. ~/.config/git/ignore) can hide the shared agent files.
for f in AGENTS.md CLAUDE.md GEMINI.md .claude/settings.json; do
  if git check-ignore -q -- "$f"; then
    src="$(git check-ignore -v -- "$f")"
    echo "FAIL $f is ignored by: ${src%%$'\t'*}"
  fi
done
user_settings="$HOME/.claude/settings.json"
if [ -f "$user_settings" ] && command -v jq >/dev/null 2>&1; then
  asks="$(jq -r '(.permissions.ask // [])[] | select(test("git (commit|push)"))' "$user_settings" 2>/dev/null || true)"
  [ -z "$asks" ] || echo "WARN $user_settings asks before: $(echo $asks). It overrides this repo's allow; agents will keep asking."
fi
for t in git gh jq make; do
  command -v "$t" >/dev/null 2>&1 && echo "ok   $t" || echo "MISS $t"
done
gh auth status >/dev/null 2>&1 && echo "ok   gh auth" || echo "MISS gh auth (run: gh auth login)"
gh auth status 2>&1 | grep -q "'project'" && echo "ok   gh project scope" || echo "MISS gh project scope (run: gh auth refresh -s project)"
leak="$(git ls-files -- material CLAUDE.local.md AGENTS.local.md .claude/settings.local.json .env)"
[ -z "$leak" ] && echo "ok   no local files tracked" || { echo "FAIL tracked local files:"; echo "$leak"; }
name="$(git config user.name || true)"; email="$(git config user.email || true)"
[ -n "$email" ] && echo "ok   identity: $name <$email>" || echo "MISS git identity (git config user.email ...)"
