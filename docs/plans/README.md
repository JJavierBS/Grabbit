# Team plans

Four plans, one per team, to build the MVP in parallel until the feature freeze (Sun 00:00
Helsinki). Each team of one human plus agents opens its own plan and works its issues in
order. Product truth lives in `docs/agents/` (challenge.md, flow.md, agent.md, api.md);
these plans only say who does what, in which order, and where teams meet.

| Team | Plan | Issues, in order | Owns |
| --- | --- | --- | --- |
| 1 Platform | `team-1-platform.md` | #21 skeleton, #29 deploy, #30 README, demo rehearsal | Makefile, Dockerfile, app shell, contract, store core, events bus, deploy |
| 2 Data | `team-2-data.md` | #22 Cala client, #23 Slush pipeline, #24 signals, #28 watcher | Everything that reads Cala, signals, watcher, scheduler |
| 3 Agent | `team-3-agent.md` | #25 self-personalizing agent, #26 report builder, #34 Context.dev (nice) | Gemini, agent, profile versions, reports |
| 4 Frontend | `team-4-frontend.md` | #32 design system (impeccable, Cala tone), #27 web app, #33 browser alerts | `frontend/src/` except `src/api/`, `PRODUCT.md`, `DESIGN.md`, styles.md |

## Milestones (Helsinki time, Saturday; move them in the team chat, not silently)
| When | Milestone | Done means |
| --- | --- | --- |
| 06:00 | M0 skeleton | #21 merged: every endpoint answers from fixtures, `make dev` and `make test lint` work |
| 10:00 | M1 parts | Cala client with recorded fixtures (#22), agent chat on FakeLLM (#25 core), design system (#32), web app on fixtures (#27 core) |
| 14:00 | M2 walking skeleton | Real path: Slush attendees -> candidates with rounds and signals -> report written by Gemini -> on screen with trust badges; a chat correction rewrites the report. First deploy (#29) |
| 18:00 | M3 proactive | Watcher, scheduler and simulated event (#28) reach the browser as a desktop notification (#33) |
| 21:00 | M4 demo-ready | Cache warmed, demo thesis fixed (open-questions D2), polish pass, full demo script rehearsed twice |
| 00:00 | Freeze | Only fixes; then video, deck, README (#30) |

## Dependency graph
```
#21 skeleton ──┬─> #22 Cala ──> #23 Slush ──┬─> #26 report ──> #28 watcher ──> #33 alerts (UI)
               ├─> #24 signals ─────────────┤
               ├─> #25 agent ───────────────┘
               ├─> #27 web app (fixtures first)      #32 design system (no dependency)
               └─> #29 deploy                         #34 Context.dev (after #26, nice)
```

## Rules for every team
- Workflow, branches, commit titles: `docs/agents/workflow.md`, `commits.md`. One issue =
  one branch = one PR. Bring main in with `git merge origin/main`, never rebase.
- Stay in your owned paths (see each plan). Touching another team's path: say it in the
  team chat first and keep the change minimal.
- Contract: `backend/app/models.py` and `api.md` change together, with
  `frontend/src/api/schema.ts` regenerated in the same PR (`npm run gen:api`). Announce it.
- Store: Team 1 owns `backend/app/store/db.py` (connection, table registry). Each team
  adds its own `store/<domain>.py` and registers its tables there, so nobody edits the same
  file.
- No real network or Gemini in tests. `CALA_MODE=replay`, `LLM_MODE=fake` work offline.
- Before every push: `make test lint`. Merge your PR yourself when green and nobody objects.
- Blocked for more than 20 minutes: post it in the team chat with the issue number.
- Before starting any work, the docs from PR #20 must be on main (stack, api.md, agent.md).
