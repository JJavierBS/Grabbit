# Pitch, deck and submission

Draft material for the README, the 5-minute peer review at the table, the deck PDF and the
final pitch. Everything marked "draft" needs a human to confirm. Facts come from
research.md and cala.md; never add figures that are not sourced there.
The video script lives in challenge.md "Demo script".

## Punchline (chosen 2026-11-14, identical in README and form)
"Slush has 2,989 attendees and you are one person. Grabbit finds the startups backed by
the investors you trust, shows the source of every fact, and alerts you when one of them
moves."

## Problem (sourced)
- User: an investor who decides alone and has neither the time nor the means to build
  automated research systems, from small private equity down (challenge.md "Who the user
  is"). The demo follows a business angel preparing Slush 2026.
- The angel's number: Slush 2026 has 2,989 attendees in Cala (2,980 companies), against one
  person. Source: warm-up of 2026-11-14 (issue #30); rerun `make warm` before quoting it.
- Same pain higher up the segment: a PE sourcing process can take three months and an
  external due diligence costs around EUR 150k (Investor B, research.md). Use as backup,
  not as the headline.
- Individual investor with capital: no time to scout new opportunities (Investor A).
- Web information is scattered and unverifiable: "who certifies a number?" (Investor B).

## Solution (draft, follows the MVP in challenge.md)
An agent that starts from a vague thesis, walks the Slush 2026 attendees in Cala's graph,
asks data-backed questions, narrows them to a shortlist and a memo, and then watches those
startups before, during and after the event until the angel finds a round. Every fact
shows its trust level and source; web signals are labelled "web, unverified". The agent
personalizes the report itself from the conversation, rewriting its own instructions. It
never tells you what to buy.

## Why Cala is core (Use of Cala, 25%)
- Every fact on screen comes from Cala's raw entity graph with source and date (cala.md).
- The agent reads each entity's introspection, so its questions grow with Cala's coverage
  (decisions.md).
- Discovery from the graph: the Slush 2026 `Event` lists its attendees; the web only adds
  colour (decisions.md 03:10).
- Signals only the graph gives: who led and co-invested in each round (`is_lead`),
  "co-invest with who you trust", "likely to raise soon" from dated headcount and rounds.
- Trust level per fact from `source_rank`, with date precision (cala.md).
- The watcher diffs Cala's dated edges (rounds, executives, headcount, acquisitions).
- Pitch line: Cala's graph finds the deal; every fact shows how much you can trust it.

## Originality (draft)
- Headline: the agent personalizes itself. Every correction or reaction in the chat makes
  Gemini rewrite its own report instructions; the report changes on screen and the history
  shows what it learned (agent.md "Self-personalization").
- An agent that asks the investor questions instead of only answering them (Investor B's
  "plan mode" analogy).
- Trust as the product: every fact shows how strong its source is (registry, company,
  press, database) and how precise its date is; "not published" is never shown as zero.
- Meet startups before their round: "likely to raise soon", not "raised last month".
- To research before claiming anything (R6 in open-questions.md): startup databases with
  saved searches and alerts (Harmonic, Specter, Crunchbase, Dealroom), generic AI chatbots.
  State the difference, not "nothing like it exists".

## Impact and implementation (event-wide judges, draft)
- Impact: many angels and small investors decide without a research team; the same engine
  serves any event in Cala or a free thesis, and small funds at a deeper level.
- Implementation: built only on public, sourced data via API; costs and data freshness are
  open questions (open-questions.md C2, C6); state them honestly.

## Business model (draft, must not contradict decisions.md)
- Options consistent with "the investor decides": subscription per seat, per memo, or per
  watched company. Commission on executed deals only as future work, without the bot buying
  (open-questions.md K1).
- Upsell idea for individuals: "what did reference investor X do in situation Y", per query
  (Investor B), depends on C7.

## 5-minute peer review at the table (draft)
One voice, in English, on the real app, no slides. The reviewer plays the investor and
drives the Grabbit laptop; we talk. Five minutes is the team's figure (the guidebook gives
none). Event-wide criteria (challenge.md): beats 3 to 7 show Innovation, the close states
Impact and Implementation. Timed twice on https://www.grabbit.cloud on 2026-11-15: thesis
to questions 14-21 s, investors to the open report 31-34 s, correction to the rewritten
report 26-37 s, bell to alert 30 s. Each wait has a line to say.

### Table setup
- Laptop A, "the pile": one Chrome window with 40 tabs, five for each of the eight startups
  in the demo report (command below; check the names against the first report of the day).
- Laptop B, Grabbit: https://www.grabbit.cloud/?demo (`?demo` adds the Alerts bell), zoomed
  so three people can read it standing. A browser that has never opened Grabbit starts the
  guided demo by itself: close its card once.
- Lids half closed until the choice. Stand next to the reviewer; never touch the keys.
- Between rounds: "New research" (Ctrl+Shift+O), close the side panel and the alert.
- Before the first round: the demo checklist below, then one full pass of this script.

```sh
tabs=()
while IFS='|' read -r name site; do
  q=${name// /+}
  tabs+=("https://$site" "https://www.linkedin.com/search/results/companies/?keywords=$q"
    "https://www.crunchbase.com/textsearch?q=$q"
    "https://www.google.com/search?q=$q+startup+funding+round"
    "https://news.google.com/search?q=$q+startup")
done <<'EOF'
Pally|pally.com
whisperr|whisperr.net
Palette|palette.team
Eka Labs AI|ekalabs.ai
Hashlist|hashlist.com
People Made Machines|peoplemademachines.com
studio vaai|studio-vaai.com
Green Factory AI|greenfactory.ai
EOF
google-chrome --new-window "${tabs[@]}"
```

### Beats
| Start | Beat | The reviewer | On screen |
| --- | --- | --- | --- |
| 0:00 | 1. You are the investor | listens | lids half closed |
| 0:20 | 2. The choice | picks a laptop | A: 40 tabs. B: "Tell me what you look for at Slush 2026." |
| 0:50 | 3. A vague thesis | taps "AI startups at pre-seed and seed" | "walking the Slush attendees in Cala...", then three questions with numbers |
| 1:25 | 4. Who you trust | types "I trust Y Combinator and 500 Global" | "From now on: ..."; the report opens by itself |
| 2:13 | 5. Every fact has a source | scrolls to Pally | "Rewritten for you", "Co-invest with investors you trust", a badge under each value |
| 2:50 | 6. Correct it, leave it watching | types "Shorter, one line per startup", presses Alerts | "From now on: one line per startup."; the report shrinks; "Alert in 30 s" |
| 3:40 | 7. The alert | reads it | "GREÏ announced a Seed, led by Y Combinator", "Simulated event" |
| 4:00 | 8. Close | | A and B side by side; done by 4:40 |

### What we say
Directions are in italics. Read the violet "From now on" notes aloud as they appear: their
wording changes from run to run.

1. *Lids half closed.* "Next week Slush opens in Helsinki. For the next five minutes you are
   not a hacker. You are a business angel: you invest your own money in young startups, and
   you work alone. No analysts. Cala, our challenge partner, lists 2,989 attendees. You
   have two days."
2. *Open laptop A.* "You can prepare like this. Forty tabs: websites, LinkedIn, funding
   databases, news. And that is only eight startups. For the whole list you would need
   about fifteen thousand." *Open laptop B.* "Or like this: one box, one sentence. Which one
   do you open first?" *Wait.* If Grabbit: "Then it is yours. You drive." If the pile:
   "Brave. Ten seconds: find me one startup backed by an investor you trust... That is the
   problem. Now try the other one."
3. "A thesis starts vague. Tap the first suggestion." *While it works:* "It is not searching
   the web. It is walking Cala's graph: the Slush event, its attendees, their funding
   rounds, and who led each one." *The questions appear.* "It does not answer yet. It asks,
   and the numbers in each question come from the graph, not from the model. Now tell it
   what matters most: who you trust."
4. "Type: I trust Y Combinator and 500 Global." *After Enter:* "Nobody can read 2,989
   companies. So you do what investors really do: borrow the judgement of people you trust.
   If a fund you respect put money into a startup, somebody already did the filtering. A
   web search cannot answer that. The funding rounds can: who invested, who led, and when."
5. *The report opens.* "There. It rewrote the report for you: a new section, 'Co-invest
   with investors you trust'. Y Combinator led Pally's seed; 500 Global led whisperr's
   pre-seed. Scroll to Pally. Under every value, a badge says where the fact comes from: a
   filing, the company, the press, a database. No data? It says 'Not published'. Never a
   zero, never a guess."
6. "Too long? There is no settings page. Tell it: type 'Shorter, one line per startup'."
   *After Enter:* "Now press the bell, top right. We cannot make a startup raise money on
   cue, so it stages one market event thirty seconds from now." *The note appears.* "'From
   now on: one line per startup.' That is not a filter. It rewrote its own instructions,
   and the next report will come this way." *The report shrinks.* "Look: shorter, and the
   startups it dropped are struck through."
7. *The alert lands.* "There. Grabbit just interrupted my pitch. A startup at Slush
   announced a seed round, led by Y Combinator: an investor you trust. It says why it
   matters. And it says 'Simulated event', because we staged this one; the check and the
   delivery are the real ones."
8. *Both laptops.* "You just ran the whole loop yourself, on real data from Cala. It is for
   every investor who decides alone: angels, search funds, small funds. One investor we
   interviewed told us: 'If a tool pre-selects and I review each pick by hand, I've already
   won.' Next week, others will be here, searching. You will be here, deciding. Grabbit
   finds the startups backed by the investors you trust, shows the source of every fact,
   and alerts you when one of them moves."

### When the clock or the app misbehaves
- Report open later than 2:30: skip the correction. "Looks right? Press the bell." Open
  "What changed" during the countdown and read its top entries, all "By Grabbit".
- Time to spare, or they want more: click a badge (it opens the source); "Why it is here"
  draws the path to the trusted investor; "What changed" shows "Its own report
  instructions", the prompt Grabbit writes for itself, with the reason and an undo.
- Type the correction. Do not tap the chip "Shorter, co-investors first": in one run the
  new summary said the instruction was not applied.
- Thesis and investors go in two messages. In one message the report came back with two
  startups under "Other matches" and a reply saying that nothing met the criteria.
- Replay mode has only Y Combinator and 500 Global warmed: another investor can leave the
  co-invest section and the alert empty.
- A question can arrive in another language (seen once): skip it and go on.
- GREÏ is not one of the eight startups in the report: say "a startup at Slush", never "on
  your shortlist".
- Gemini or the server is down: do not reload. "How Grabbit works", at the foot of the
  sidebar, runs the same loop on sample data inside the browser, with no server (start it
  once before the first round so it is loaded). Say that it is sample data.
- A reviewer in a hurry: beats 1 and 2, then "See how it works" (1 min) with "Show me".

### If they ask
- "Is the alert real?" No, and the screen says so. Cala has no push: the watcher polls the
  shortlist every 15 minutes and compares it with the last snapshot. The demo stages one
  change and sends it through the same comparison, importance check and delivery (flow.md 4).
- "Why not ask a chatbot?" It searches the web and writes its own figures. Grabbit walks
  the funding rounds from the investors you trust, shows every fact with its source and how
  strong it is, and keeps watching. Startup databases with alerts exist (open-questions.md
  R6): state the difference, never "nothing like it exists".
- "How do you search 2,989 attendees?" Not in list order. It starts from the trusted
  investors' rounds and keeps the companies that attend. With Y Combinator and 500 Global
  that found 27 startups backed by them, against 5 in the first 150 attendees
  (docs/algorithm.md).
- "Does it pick for me? How do you earn?" It never says what to buy; the investor decides.
  A subscription per seat or per watched company ("Business model" above).

## Deck outline (PDF, about 8 slides)
1. Name, punchline, team.
2. Problem and user, with the two interview quotes (pseudonymised).
3. Solution: the flow in one picture.
4. Demo screenshots: thesis -> questions -> shortlist -> memo -> alert.
5. Why Cala: discovery from the Slush event, round leads, trust level per fact.
6. Validation: interviews with two investors.
7. Business model and what is next.
8. Technologies and links (demo, repo, video).

## Demo checklist (before every live demo, rehearsal or recording)
- [ ] `make warm` with live Cala on the laptop or server that will present (without
  `--limit`). It ends with the first chat turn's own walk and prints
  `first chat turn: N Cala calls, 0 cache misses`. A cold first turn took about 200 s in
  the 14 Nov audit, because Cala answered 429 about 100 times; warmed, it reads only the cache.
- [ ] `make warm ARGS=--check` right before presenting: it exits 1 on any miss.
- [ ] Start from a fresh workspace (new browser profile or cleared site data). A browser that
  has never opened Grabbit starts the guided demo by itself (#184): close its card first, then
  type the demo thesis (decisions.md "demo thesis").
- [ ] Before the staged `grei_seed_round` alert, verify GREÏ is in the displayed shortlist.
  Add FIRSTPICK to the trusted investors if needed. Close the report on narrow screens,
  then press Alerts and check its countdown. Full rehearsal: `docs/demo-rehearsal.md`.

## Submission checklist (challenge.md "Submission form needs")
- [ ] Punchline chosen and identical in README and form.
- [ ] README: Problem, Solution, Demo links, Technologies used, Team roles.
- [ ] Video max 2:00, public on YouTube or Vimeo, simulated event labelled.
- [ ] Deployed demo link works from a clean browser.
- [ ] Deck PDF uploaded.
- [ ] Repo public, MIT licence, link in the form.
- [ ] Credit choice, phone numbers, Discord usernames.
- [ ] Status switched from DRAFT to FINAL before Sun 10:00.
- [ ] All four present for peer review from Sun 10:30.
