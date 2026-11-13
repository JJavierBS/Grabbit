# Shared patterns for the git hooks. Edit here to extend.
LOCAL_PATHS='(^|/)(material/|CLAUDE\.local\.md$|AGENTS\.local\.md$|\.claude/settings\.local\.json$|\.claude/worktrees/|\.env$|\.env\.(local|development|production|test)$|\.env\.[^/]*\.local$)'
ATTRIB='co-authored-by:.*(claude|anthropic|copilot|openai|chatgpt|codex|gemini|cursor)|generated (with|by) .*(claude|chatgpt|copilot|codex|gemini|cursor|ai\b)|claude-session:|claude\.ai/code|🤖'
SECRETS='sk-ant-[A-Za-z0-9_-]{20,}|sk-(proj-)?[A-Za-z0-9_-]{32,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}|AIza[0-9A-Za-z_-]{35}|xox[abprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
PROTECTED_BRANCH='main'
COMMIT_SUBJECT='^\[[A-Za-z0-9-]+\] \[[A-Z]+!?\]( \(#[0-9]+\))? [^ (].*[^.]$'
GIT_GENERATED_SUBJECT='^(Merge |Revert ")'
