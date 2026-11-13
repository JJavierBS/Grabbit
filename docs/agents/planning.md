# Planning: from challenge to backlog

Use when asked to turn `challenge.md` into issues. Output is issues on GitHub, not a document.

1. Read `challenge.md`, `architecture.md` and `decisions.md`. Ask a human for any TODO that
   blocks the plan (track, MVP, demo script).
2. Derive work backwards from the demo script: every demo step needs its backend, frontend
   and data pieces working end to end. Anything not needed by the demo gets `prio:nice`.
3. First issues, in this order, so the team can split up fast:
   - Contract: API/shared types and mocks (unblocks front and back in parallel).
   - Walking skeleton: one demo step working end to end, deployed.
   - Then one issue per demo step and area.
4. Each issue: one PR, finishable by one agent in under ~2 hours, clear acceptance criteria
   that become tests, label `area:*` and `prio:demo` or `prio:nice`, milestone if time-bound.
   Mark dependencies in the body (`Blocked by #n`).
5. Create them with the task template fields:
   `gh issue create --title "<imperative title>" --label "area:backend,prio:demo,type:feature" --body-file <tmp.md>`
   Body sections: `### Goal`, `### Acceptance criteria` (checkboxes), `### Area`, `### Context`.
6. Put ready issues on the board: `scripts/board.sh <n> "Ready"`.
7. Reply with a table: number, title, area, priority, depends on. Nothing else.
