# Contributing

How the team works on Grabbit. Agents follow [AGENTS.md](../AGENTS.md); humans start here.

After cloning, run `bash scripts/setup.sh` once (hooks, local exclusions, `.env`).
Then follow `AGENTS.md`: one issue, one branch, one PR; never push to `main`.
Raw briefs and partner docs live in `docs/reference/`; refresh a docs mirror with
`bash scripts/fetch-docs.sh [base_url] [dest]` (default: Context.dev).
How we manage issues, the board, labels and milestones: [docs/agents/workflow.md](agents/workflow.md).

Commit messages and PR titles: `[<github-user>] [<TYPE>] (#<issue>) <Summary>`, e.g.
`[JJavierBS] [FEATURE] (#12) Add Cala API wrapper`. TYPE is FEATURE, FIX, DOCS, CHORE...
Leave out `(#<issue>)` only when there is no issue. Details in [docs/agents/commits.md](agents/commits.md).

**Important: no AI attribution anywhere.** Commits, PR titles and descriptions, branch
names, issues and code comments must not mention AI tools: no `Co-Authored-By` trailers
for assistants, no "Generated with ...". The `commit-msg` hook rejects them; configure
your assistant so it does not add them.

