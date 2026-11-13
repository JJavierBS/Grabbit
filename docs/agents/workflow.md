# Workflow

All work is tracked as GitHub issues on the project board "Grabbit board". The board is the
source of truth for who does what. No issue, no work: create one first, even for small tasks.

## How the project is managed
- Board status: Backlog (not refined) -> Ready (clear acceptance criteria, free to take) ->
  In progress (assigned, branch exists) -> In review (PR open) -> Done (merged).
  Move items with `scripts/board.sh <n> "<Status>"`; it reads `.github/project.env`.
  New issues and PRs are auto-added to the board; closed issues move to Done on their own.
- Board field Priority: `P0 demo`, `P1 should`, `P2 nice`.
- Labels, every issue has one `area:*`, one `type:*` and one `prio:*`:
  - `area:backend`, `area:frontend`, `area:design`, `area:infra`, `area:pitch`, `area:docs`
  - `type:feature`, `type:bug`, `type:chore`
  - `prio:demo` (needed for the live demo), `prio:nice` (only if time allows)
  - `blocked`: waiting on someone or something; say on what in a comment.
- Milestones: `Pre-submission` (Fri 23:59), `Feature freeze` (team decides; only fixes,
  polish, video and deck after it), `Final submission` (Sun 10:00, set FINAL by 09:30).
- Submission chores (README, deploy, deck, video, final form, rehearsal) already exist as
  issues under those milestones: `gh issue list --milestone "Final submission"`.
- Issue templates: Task and Bug (`.github/ISSUE_TEMPLATE/`). Body sections: Goal,
  Acceptance criteria (checkboxes, each one becomes a test), Area, Context.
- Dependencies go in the issue body: `Blocked by #n`.
- One issue = one branch `<n>-<slug>` = one PR with `Closes #<n>`. Commit and PR title
  format in commits.md. `main` only changes through squash-merged PRs.

## Plan
Turning the challenge into issues: see planning.md.

## Start a task
1. Read the issue, not a pasted summary: `gh issue view <n> --comments`
2. Assign and move it: `gh issue edit <n> --add-assignee @me` then
   `scripts/board.sh <n> "In progress"`
3. Branch from fresh main, linked to the issue:
   `git fetch origin && gh issue develop <n> --base main --name <n>-<short-slug> --checkout`
4. Unclear acceptance criteria: ask in the issue (`gh issue comment <n>`), do not invent them.

## While working
- Small commits, one purpose each (see commits.md).
- Bring in main with `git merge origin/main`, not rebase (rebase would need force-push).
- New work found along the way: `gh issue create` with label `area:*`, do not widen this PR.

## Finish
1. `make test lint` passes locally. New behaviour has tests (see testing.md).
2. Log any design choice in `decisions.md`.
3. Push and open the PR:
   `git push -u origin HEAD && gh pr create --fill --body "Closes #<n>"`
   Fill the PR template; the title becomes the squash commit, so it follows commits.md.
4. `scripts/board.sh <n> "In review"`
5. Merge when green and nobody objects: `gh pr merge --squash --delete-branch`
   Closing the issue moves it to Done automatically.

## Parallel agents
- One agent session per issue. Start a fresh session for the next issue instead of
  continuing a long one; the issue and these docs carry the context.
- Each parallel agent works in its own worktree and branch. Never share a working tree.
- Two issues touching the same files: say so in both issues before starting.
