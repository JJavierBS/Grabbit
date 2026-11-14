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
| D1 | Which single path is the demo? flow.md covers portfolio watching (listed shares, startup stakes) and the thesis-to-memo flow; challenge.md "Scope" makes both MVP | Execution (25%): "one need solved brilliantly beats many solved halfway" (Cala brief). Two full flows in a weekend is the main execution risk | One investor, one thesis: thesis -> data-backed questions -> verified shortlist -> watcher on that shortlist. Portfolio watching becomes the same watcher on the shortlist, not a second flow |
| D2 | Demo country, subsector and the 5-10 demo companies | Cala data is rich for UK (Companies House) and France (INPI) only; Spain and Finland have registry basics (research.md "Cala coverage") | UK, a fragmented subsector of mid-sized private firms; probe each company's introspection before choosing |
| D3 | Demo persona: hobby investor with listed shares and startup stakes (flow.md onboarding, video script) or small private equity / search fund (acta recommendation, Investor B)? | Investor B advised against startups (little data); listed shares and UK SMEs need different Cala paths | Small PE / search fund; mention the hobby investor as the same engine at a lighter depth (research.md "Who the user could be") |
| D4 | Stack: language, frameworks, LLM provider and model, storage, scheduler, hosting of the demo link | architecture.md, api.md, backend.md, frontend.md, testing.md and the Makefile are all TODO; the agent and the importance check need an LLM (flow.md section 4), with no env var yet | Pick what the team knows best; one repo, one `make dev` |
| D5 | Context.dev role: soft signals only (decisions.md, challenge.md Scope) or also company discovery? | Cala cannot list companies by criteria (cala.md), so the thesis flow needs a discovery source; research.md says "discovery comes from the web" | Context.dev `company/search` discovers candidates; Cala verifies every fact and is the only source of facts. Soft signals stay labelled "web, unverified". Wait for Cala's answer on `knowledge/query` (C1) |
| D6 | Compete in the Context.dev challenge too? | One submission can enter several challenges (guidebook p. 11). Its criteria are not in the repo | Read its brief (hackjunction.app challenge 332 and tech challenge 44), distil it into context-dev.md, then decide |
| D7 | Feature freeze time and explicit out-of-scope list (challenge.md) | Without them the MVP keeps growing | Freeze Sat evening; out of scope: whatever D1 drops |

## Conflicts between docs
| Id | Conflict | Where | To resolve |
| --- | --- | --- | --- |
| K1 | Business model "commission on analyses that end in a purchase, even executing it from the bot" vs "the agent never recommends what to buy" | research.md "Business model ideas", acta; decisions.md | Pitch a model that keeps the investor deciding (subscription, per-memo or per-seat). A commission on executed deals can be listed as future, never with the bot buying |
| K2 | Context.dev "soft signals only" vs web discovery | decisions.md, challenge.md, research.md | D5 |
| K3 | Persona and holdings | flow.md onboarding, challenge.md demo script vs acta | D3 |
| K4 | Context.dev status "being evaluated, not a dependency" vs MVP using it | context-dev.md vs challenge.md Scope | Fixed in this audit: status and `.env.example` updated; role still D5 |

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
| R1 | Live demo or a judge's question goes outside the cache and hits a 429 or a multi-minute call | A call budget per demo step; pre-warm every node on the demo path; for an unexpected company, show what is cached and say live lookups are rate-limited |
| R2 | The mocked alert is discovered by a judge and read as faked execution | Label it on screen and in the README as "simulated event" (the fixture is already separate, flow.md section 5); say it aloud in the live demo |
| R3 | No real Cala change exists for the demo companies, so the watcher shows nothing real | Pick, during D2, at least one company with a recent dated event (funding round, ownership change, filing) and replay it from the snapshot |
| R4 | Deployed demo link: desktop notifications need a browser tab and permission; the Cala key must stay server-side | Server-side calls only; the deployed link can run in cached mode |
| R5 | The video shows the least original part (digest, alert) and no "verified by Cala" moment | Fixed in this audit: the demo script now shows source labels; consider a few seconds of the thesis flow |
| R6 | Originality: no comparison with existing tools | pitch.md lists the alternatives to research; do not claim "nothing like it exists" without checking |
| R7 | Impact and Implementation (event-wide judges) are not argued anywhere | pitch.md drafts both; needs numbers the team can defend |

## Submission status unknown
- Was the Fri 23:59 pre-submission draft sent with the Cala challenge? Someone confirm.
- Peer review time: the guidebook says Sun 10:30-14:00; the platform listed a different end
  in earlier reads. Plan to be available until 14:00.
