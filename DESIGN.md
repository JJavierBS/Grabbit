---
name: Grabbit
description: A proactive research agent for business angels. Afterglow - a light, quiet room with one violet light, taken from the Grabbit logo.
colors:
  violet: "#6139f8"
  violet-light: "#5530e8"
  ground: "#f7f7fa"
  surface: "#ffffff"
  surface-raised: "#ffffff"
  panel-strong: "#ecebf3"
  ink: "#14151c"
  text: "#2a2b36"
  text-muted: "#5c5d6e"
  text-faint: "#737485"
  on-ink: "#ffffff"
  border: "#8e8fa3"
  border-soft: "#e3e3ec"
  focus: "#6139f8"
  info: "#1f5fbf"
  info-bg: "#e6efff"
  marker: "#6139f8"
  marker-soft: "#ece7ff"
  warning-ink: "#4b25d6"
  danger: "#b42318"
  danger-bg: "#fde8e6"
typography:
  display:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "2rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  lead:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.625
  small:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.375
  label:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.5
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  xl: "24px"
  pill: "999px"
spacing:
  "1": "4px"
  "2": "8px"
  "3": "12px"
  "4": "16px"
  "5": "20px"
  "6": "24px"
  "8": "32px"
  "10": "40px"
  "12": "48px"
  "16": "64px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  composer:
    backgroundColor: "{colors.surface-raised}"
    rounded: "{rounded.xl}"
    padding: "8px 8px 8px 16px"
  chat-user:
    backgroundColor: "{colors.panel-strong}"
    textColor: "{colors.ink}"
    rounded: "{rounded.xl}"
    padding: "8px 16px"
  report-outline:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "16px 20px"
  side-panel:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
  rewrite-banner:
    backgroundColor: "{colors.marker}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.md}"
    padding: "12px 16px"
  change-note:
    backgroundColor: "{colors.marker-soft}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  toast-alert:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "16px"
---

# Design System: Grabbit

## Overview

**Creative North Star: "Afterglow"**

A light, quiet room with one violet light, and the light moves only while the agent works
or listens. The violet and the night ink (#14151c) come from the Grabbit logo. The first
build was black; the team asked for a lighter page on 2026-11-14, so the page is now light
only.

The surface is an Operate surface in the manner of a minimal AI chat. One centred column
holds the conversation. A report shows in that column as a short outline card, and the
full report opens in a side panel on the right, in the manner of an artifact panel. The
same panel holds "Reports" (every past report) and "What changed". Below 64rem the panel
covers the screen. Everything must stay easy: few controls, plain words, one action at a
time.

Decided on 2026-11-14 (#53); it replaces the cala.ai cream tone. Shipped code wins where
this file and the code differ.

**Key Characteristics:**
- Near-white ground, white panels, night-ink text. Violet is light, never decoration.
- One sans (Hanken Grotesk) for everything. Rank comes from weight and size.
- The agent speaks in plain text with no bubble. The user's lines sit in a soft grey pill.
- Flat surfaces separated by soft rules and soft ink shadows. The only coloured glow is the
  violet light.

## Colors

### Primary
- **Violet** (#6139f8): the light. It glows under the composer, edges a new report
  outline and the alert toast, fills the "Rewritten for you" banner (white text) and the
  pressed Talk button, and colours the logo mark. 6.1:1 on white.
- **Violet light** (#5530e8): violet as small text or a thin line (the "Open report"
  link, the caret, the "Live" dot).

### Neutral
- **Ground** (#f7f7fa): the page and the chat column.
- **Surface** (#ffffff): the side panel, the report outline card, the composer, cards.
- **Panel strong** (#ecebf3): user message pills, neutral badges, hover and pressed fills,
  skeleton bones.
- **Ink** (#14151c): headings and primary buttons. **Text** (#2a2b36): body.
  **Text muted** (#5c5d6e): meta, at any size. **Text faint** (#737485): list markers.
- **Border** (#8e8fa3): field and secondary button edges, 3:1 on white. **Border soft**
  (#e3e3ec): rules and card edges.

### Support
- **Info** (#1f5fbf on #e6efff): the Press trust badge.
- **Marker soft** (#ece7ff) with **warning ink** (#4b25d6): the violet wash on changed
  report parts, the chat change note, warning badges, text selection.
- **Danger** (#b42318 on #fde8e6): errors only.

### Named Rules
**The One Light Rule.** Violet means "the agent did something or listens": it works, it
changed the report, it raised an alert, it hears you. Never use it for decoration.

**The Trust Ladder Rule.** Trust strength reads from fill weight before hue: solid ink,
ink outline, blue tint, grey tint, dashed violet, dashed empty. A judge on a washed-out
projector, or without colour vision, must still rank the six badges.

## Typography

**Font:** Hanken Grotesk Variable, self-hosted with `@fontsource-variable` so the demo
works offline.

### Hierarchy
- **Display** (600, 2rem, -0.02em): the report and history titles.
- **Title** (600, 1.5rem, -0.02em): section titles and startup names.
- **Lead** (400, 1.25rem): the report summary.
- **Body** (400, 1rem, 1.625): chat text and report prose, 65ch max.
- **Small** (400, 0.875rem): meta, outline sections, panel title.
- **Label** (500, 0.75rem): badges and small buttons.

Numbers use tabular figures everywhere.

**Logo:** `components/Logo.tsx`, also `public/favicon.svg`. Violet speed lines, the
night-ink rabbit whose head is a G, and the wordmark in Outfit 800 (`--font-logo`, the
closest open face to the logo lettering; used for the wordmark only). The mark is drawn as
vector from the logo artwork, because the source PNG is a glow render on black that cannot
be cut out cleanly. Replace it with the original vector when the team has one.

## Layout

- **Sidebar (left):** `--sidebar-width` (17rem), `--color-sidebar` fill, soft right edge.
  The logo and a close button at the top, then "Reports" grouped by day ("Today",
  "Yesterday", a date), in the manner of a conversation list. It collapses on wide screens
  (remembered in the browser) and becomes a drawer with a scrim below 64rem.
- **Top bar:** an "Open sidebar" button and the logo only while the sidebar is hidden, the live
  the live status, then "Alerts" (demo only) and "What changed" on the right as small ghost
  buttons. No border, no other labels.
- **Chat:** one column, 44rem max, centred while the panel is closed. Composer at the
  foot with suggestion chips above it.
- **Side panel:** shares the workspace with the chat at 1.3 : 1, the chat never under 24rem, surface fill, soft left edge, 14px top-left
  corner, sticky bar with the panel name and a close button. It slides in from 2rem right
  in 280ms. Escape and the close button close it, and focus returns to the opener. Below
  64rem it is fixed full screen.
- **Phone (375px):** the top bar wraps its actions to a second row; the panel covers the
  screen.

## Elevation & Depth

Flat by default. The side panel and cards sit on soft 1px edges. The large shadow pairs
a soft ink drop with a 1px soft edge. The glow tokens (`--glow-rest`, `--glow-work`) fall
from below with a negative spread, like the logo's light, and only the composer, the
report outline and the alert toast carry them.

## Components

### Composer (signature)
A white capsule, 24px corners, soft edge, resting violet glow below. The field inside has
no frame of its own. Focus turns the edge violet. While the agent works or listens, the
edge turns violet and the glow breathes between rest and full every 1.6s. Under reduced
motion it holds the full glow without motion. Inside, right to left: the round primary
(ink) send button and the round Talk button.

### Talk (press to talk)
A round ghost button with a microphone. Press it and it turns violet with a stop square;
the browser's speech recognition writes into the message box as the user speaks. Press it
again (or send) to stop. The text stays in the box for the user to read and send, so a
misheard word never reaches the agent unseen. Browsers without speech recognition do not
show the button. A blocked microphone shows a one-line error above the chips.

### Report history (sidebar)
Every report from `GET /api/reports`, newest first, grouped by day. Each row: the report
summary on one line (14px medium ink, ellipsis), then "Latest" on the newest, the time,
the number of startups and the profile version (12px muted). Hover fills the row with
`--color-sidebar-hover`; the report open in the panel is a white raised row with
`aria-current`. Opening the newest shows the live report; an older one opens read only
(no confirm, no "Run now") as "Past report".

### Report Outline (signature)
The report as it shows in the chat: the report title (16px semibold), a meta line (date,
number of startups, profile version), the numbered section list above a soft rule, and an
"Open report" link in violet light. The whole card is the click target; the button keeps
`aria-expanded` and `aria-controls="report-panel"`. A new version lands with a violet
edge and the full glow, fading to rest in 1.2s. After a rewrite it carries a
"Rewritten" badge.

### Chat Messages
Agent text: plain, 16px, no bubble. User text: panel-strong pill, 24px corners, right
aligned, 80% max.

### Change Note
Marker soft fill, 1px violet border, sparkles icon, ink text, an "Undo" button on the
newest change.

### Rewrite Moment
When the report rewrites itself, the panel opens on it. A solid violet "Rewritten for
you" banner names the changes, changed parts get the marker-soft wash and a "New",
"Moved" or "Rewritten" badge, removed parts are struck through. The marks hold 4s.

### Trust Badge
Six pills with a Lucide icon and the agent.md label, ranked by the Trust Ladder Rule.

### Alert Toast
Bottom right, white, violet edge, large shadow plus the full glow, ink text, "Open in
chat" as a small ink pill. It stays until dismissed and uses `role="alert"`. In the demo,
"Alerts" in the top bar fires the simulated alert 30 s after the click, so it lands like a
real one; the alert itself still carries the "Simulated event" label.

### Buttons
Pills. Primary: ink fill, black text. Secondary: border outline. Ghost: no fill, panel
strong on hover and when pressed (`aria-pressed`).

## Do's and Don'ts

### Do:
- **Do** take every value from `frontend/src/styles/tokens.css`.
- **Do** show a Trust Badge next to every fact, and "Not published" when Cala has no value.
- **Do** check every new text colour for 4.5:1 on #f7f7fa and on white.
- **Do** keep one primary (ink) button per view.

### Don't:
- **Don't** use violet for anything that is not the agent acting or listening.
- **Don't** add a second typeface, gradients on text, or glass.
- **Don't** add a dark theme, or a "Demo data" label.
- **Don't** put agent text in bubbles, or a report beside the chat before the user opens it.
- **Don't** use Cala's logo, wordmark or copy.
