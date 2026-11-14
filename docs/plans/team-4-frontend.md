# Team 4: Frontend (design system, web app, alerts)

Mission: one screen a judge understands in seconds, that feels at home at Cala's founders
and investors event, where the report visibly rewrites itself and every fact shows how
much to trust it.

Read first: `docs/agents/frontend.md`, `styles.md`, `agent.md` "Trust scale" and
"Self-personalization", `api.md`, challenge.md "Demo script".

## Owned paths
`frontend/src/` except `src/api/` (Team 1's client; add query hooks in
`src/api/hooks/`), `PRODUCT.md`, `DESIGN.md`, `docs/agents/styles.md`.

## 0. #32 Design system with impeccable, in Cala's tone (start now, merge by 10:00)
Use the impeccable skill for all design work (`/impeccable` in Claude Code). It loads
project context with `.claude/skills/impeccable/scripts/impeccable context`; follow it.
1. `/impeccable init`: write `PRODUCT.md`. Product: Grabbit, a proactive research agent.
   User: a business angel preparing Slush 2026. Surface mode: Operate (app UI, scanability
   first). Brand commitment, pinned: the visual tone of cala.ai (the brief wins over the
   skill's own taste). Grabbit keeps its own name and mark; never use Cala's logo,
   wordmark or copy, and never make it look like a Cala product.
2. Capture the evidence from https://cala.ai with the browser tools (Claude in Chrome or
   the built-in browser): the home page and one or two inner pages, at 1440px and 375px.
   Read computed styles with a page script: `:root` custom properties, background, text,
   accent and border colours, font families and the size/weight/line-height of h1-h3 and
   body, radius, shadows, spacing rhythm, transition durations and easing. Save
   screenshots and raw values under `material/design/cala/` (local, not committed).
3. Read the tone of voice from their headings and copy: how they talk about data, trust
   and sources. Write it down as observed, with two or three quoted examples.
4. Write `DESIGN.md` from that evidence, in impeccable's format: palette, typography (if
   their font is not open-licensed, name the closest open font), spacing scale, radius,
   elevation, motion, iconography, voice. Note what Grabbit adds on top: the six trust
   badge variants, the "changed" highlight, the simulated-event label.
5. Tokens in `frontend/src/styles/tokens.css` (CSS custom properties, light and dark if
   cala.ai has both); raw values live only there. Fill styles.md "Design system".
6. Base components: Button, Card, Badge, `TrustBadge` (filing, primary, press, aggregator,
   web_unverified, not_published), Input, Toast, Skeleton. AA contrast, visible focus,
   375px and 1920x1080 (projector).

## 1. #27 Web app (start once #21 is merged; core by 10:00 on fixtures, done by 14:00)
Build with `/impeccable` on the pinned direction from step 0, Operate mode.
- Layout: chat on one side, current report on the other; one primary action at a time.
- Chat: history, input, the agent's "From now on: ..." note on profile changes, undo.
- Report: candidates, rounds with lead and co-investors, signals with their explanation,
  `FactValue` (value, unit, date at its precision, "not published").
- The originality moment: when a `report` event arrives after a correction, highlight what
  changed (sections reordered, startups removed or added, shorter text) for a few seconds,
  under 300ms motion. This is the shot the video needs; make it obvious.
- Profile history panel from `/api/profile/history`: what the agent rewrote and why.
- Loading, empty and error states everywhere; never a blank screen.
- Tests (Vitest): `TrustBadge` per level, `FactValue` for precision and not published, the
  change note, the changed-highlight logic.

## 2. #33 Alerts in the browser (start at M2, merge by 18:00)
`EventSource` hook in `src/api/hooks/`, reconnect on drop; toast per alert; desktop
notification when the tab is hidden, permission asked when the first report is confirmed;
clicking opens the alert in the chat with its facts; a visible "simulated event" label when
`simulated=true`. Tests with a fake EventSource.

## 3. Finish (from M4 to freeze)
- `/impeccable extract` on `frontend/src`: consolidate repeated values and components into
  the tokens and base components.
- `/impeccable audit` then `/impeccable polish` on the demo path, at 1920x1080 and 375px,
  in bounded passes. Optionally run the `impeccable-finish-reviewer` agent once.
- `/impeccable document` to sync `DESIGN.md` with what shipped.
- Take the screenshots for the deck (thesis -> questions -> shortlist -> rewrite -> alert).
