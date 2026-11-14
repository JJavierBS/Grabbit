# Open questions and conflicts

What is still undecided or contradictory, from an audit of these docs against the judging
criteria (challenge.md) on 2026-11-14. Check here before planning or building; when one is
settled, log it in decisions.md, fix the docs it touches and delete it here.
Ids are stable: reference them in issues and PRs (`see open-questions.md D2`).
"Proposal" is a suggestion from the audit, not a team decision. Do not build on it until a
human confirms.

## Team decisions that block the build
| Id | Question | Why it matters | Proposal |
| --- | --- | --- | --- |
| D5 | Discovery outside events: a free thesis with no `Event` to start from | The demo discovers from the Slush `Event` (decisions.md 03:10); outside events Cala cannot list companies by criteria (cala.md) | Team talks to Cala (C1, C3). Fallback: widen through the graph from the reference investors' rounds |
| D6 | Compete in the Context.dev challenge too? | One submission can enter several challenges (guidebook p. 11). Its criteria are not in the repo | Read its brief (hackjunction.app challenge 332 and tech challenge 44), distil it into context-dev.md, then decide |

## Conflicts between docs
| Id | Conflict | Where | To resolve |
| --- | --- | --- | --- |
| K1 | Business model "commission on analyses that end in a purchase, even executing it from the bot" vs "the agent never recommends what to buy" | research.md "Business model ideas", acta; decisions.md | Pitch a model that keeps the investor deciding (subscription, per-memo or per-seat). A commission on executed deals can be listed as future, never with the bot buying |
| K4 | Context.dev status "being evaluated, not a dependency" vs MVP using it | context-dev.md vs challenge.md Scope | Fixed in this audit: status and `.env.example` updated; role is soft signals (decisions.md 03:10) |

## Questions for Cala (workshop Sat 11:00 or mentors)
- C1 May `knowledge/query` be used only to obtain seed ids? (cala.md) Partly answered 14 Nov: at the workshop Cala recommended it for "latest news regarding <company>", which we use for news (#74); seeds still open.
- C2 Exact rate limit, whether it is raised for the hackathon, and whether multi-minute latency on hub nodes is expected (cala.md "Rate limits and latency").
- C3 A recommended way to list companies by industry or country from the graph. Partly answered by the field guide: an `Event` entity (Slush 2026) lists its attendees (cala.md "Traversal flow"); industry and country listing still open.
- C5 Do they object to Context.dev as a discovery and soft-signal source next to Cala?
- C6 How fresh is new data (a new filing or ownership change): hours, days? The watcher depends on it.
- C7 Do they hold funds' public-equity holdings (Investor A's "big fish" idea)?
- C8 UK activity codes and directors: available or planned?
- C9 What makes "use of Cala" score high for them, and what did they mean by "things web search can't" (workshop description)?

## Risks without a plan yet
| Id | Risk | Proposal |
| --- | --- | --- |
| R1 | Live demo or a judge's question goes outside the cache and hits a 429 or a multi-minute call | Cala will raise the limit (decisions.md 03:10); still pre-warm the Slush attendees and the demo path, and show what is cached for an unexpected company |
| R2 | The mocked alert is discovered by a judge and read as faked execution | Label it on screen and in the README as "simulated event" (the fixture is already separate, flow.md section 5); say it aloud in the live demo |
| R3 | No real Cala change exists for the demo companies, so the watcher shows nothing real | The video uses the staged `grei_seed_round` (labelled simulated, R2). For a real one: warm the AI attendees again later and let the watcher diff them |
| R4 | Deployed demo link: desktop notifications need a browser tab and permission; the Cala key must stay server-side | Server-side calls only; the deployed link can run in cached mode |
| R5 | The video must show the originality: the report rewriting itself after a correction | Demo script step 4 shows it; keep the profile history one click away for Q&A |
| R6 | Originality: no comparison with existing tools | pitch.md lists the alternatives to research; do not claim "nothing like it exists" without checking |
| R7 | Impact and Implementation (event-wide judges) are not argued anywhere | pitch.md drafts both; needs numbers the team can defend |
| R8 | The chat's free graph walk (#73) only replays offline for the three questions cached on 14 Nov; Gemini phrases differently or picks other entities and that part falls back to report-only | Rehearse with the exact wording: "Who led GREÏ's pre-seed, and what else have they backed?", "What else has Y Combinator invested in?", "Who founded Y Combinator, and what else are they linked to?"; or warm new questions live before recording |
| R9 | Cala news (#74) is sparse and unstable: only Hashlist (3), whisperr (2) and Palette (1) have news; for GREÏ, Vectis.ai, People Made Machines and studio vaai Cala returned a profile row instead of news, and the cache freezes whichever answer came first | Pick demo startups that have news; re-run `python -m scripts.warm --news --retry-empty` before recording |
| R10 | Hidden links (#75) are sparse on the demo thesis: of the AI pre-seed/seed attendees only GREÏ (FIRSTPICK co-invested 2× with 500 Global) and Pally (Pioneer Fund co-invested with Y Combinator) have one; founder-background links were dropped because Cala's Person nodes link only to the current company | Show GREÏ or Pally in the demo; Gemini does not see links yet, so the report text never mentions them |

## Known issues and polish (after #73, #74 and #75, 14 Nov)
Found while integrating and checking the three features in the browser. Not built; open an
issue per item before working on it.
| Id | Issue | Where | Fix |
| --- | --- | --- | --- |
| P1 | Fixed in #107: the shell clips (`overflow: clip`) and the chat log and side panel are positioned, so visually hidden labels no longer grow the document | `App.module.css`, `ChatPanel.module.css` | Pinned by `frontend/src/layout.test.ts` |
| P2 | In the explored graph, Cala's two entities "500 Global" and "500 Global (500 Emerging Europe)" both show, and only the second is marked "you trust" | `frontend/src/features/chat/openui/ExploredGraphView.tsx`, trusted set | Match trusted investors by normalised fund name as `app/discovery/links.py` does, not only by entity id |
| P3 | Fixed in #115: edge labels, stages and sectors showed raw Cala values ("is_lead", `PRE_SEED`) | `frontend/src/lib/humanize.ts`, used by the graphs, cards and `FactValue` | Pinned by `lib/humanize.test.ts` |
| P4 | Fixed in #116: edge labels overlapped the lines, and the graphs scaled text down to about 7px | `ExploredGraphView`, `CalaPath`, `components/GraphText.tsx` | Labels sit on plates; the SVG draws at 1:1 and switches to the tree when it does not fit; pinned by `ExploredGraphView.test.tsx` and `CalaPath.test.tsx` |
| P5 | `alerts.test.tsx` fails on machines whose Node/ICU formats €8M as "€8.0M" or "8 M €" (es-ES); it was already failing before #73-#75 | `frontend/src/features/alerts/alerts.test.tsx`, money formatter | Fix the formatter's locale (or the test's), so `make test` is green on every laptop |
| P6 | `scripts/board.sh` fails: `.github/project.env` does not exist, so the board cannot be moved from the CLI; #73, #74, #75 never moved | `.github/project.env` | Whoever set up the board adds the file, or move items by hand |
| P7 | `make gen-api` reads whatever backend answers on :8000, which may be another checkout's | `Makefile`, api.md | Generate from `create_app().openapi()` dumped to a file (api.md describes the workaround) |
| P8 | Agent worktrees left on the main laptop: `Grabbit/.claude/worktrees/agent-*` (branches 73-, 74-, 75-...), already merged | local only | `git worktree remove` each one once nobody needs their local databases |

## Submission status unknown
- Was the Fri 23:59 pre-submission draft sent with the Cala challenge? Someone confirm.
- Peer review time: the guidebook says Sun 10:30-14:00; the platform listed a different end
  in earlier reads. Plan to be available until 14:00.
