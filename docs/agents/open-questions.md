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
- C1 May `knowledge/query` be used only to obtain seed ids? (cala.md)
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

## Submission status unknown
- Was the Fri 23:59 pre-submission draft sent with the Cala challenge? Someone confirm.
- Peer review time: the guidebook says Sun 10:30-14:00; the platform listed a different end
  in earlier reads. Plan to be available until 14:00.
