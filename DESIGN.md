---
name: Grabbit
description: A proactive research agent for business angels. Afterglow - a black room with one violet light, taken from the Grabbit logo.
colors:
  violet: "#6139f8"
  violet-light: "#a593ff"
  ground: "#000000"
  surface: "#0e111a"
  surface-raised: "#161a26"
  panel-strong: "#1d2230"
  ink: "#f4f3fa"
  text: "#d9d8e3"
  text-muted: "#a3a2b2"
  text-faint: "#807f90"
  on-ink: "#000000"
  border: "#60657c"
  border-soft: "#262b3c"
  focus: "#a593ff"
  info: "#9db4ff"
  info-bg: "#141b33"
  marker: "#6139f8"
  marker-soft: "#1f1745"
  warning-ink: "#a593ff"
  danger: "#ff8a7a"
  danger-bg: "#2b1210"
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
    textColor: "{colors.ink}"
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

A black room with one violet light, and the light moves only while the agent works. The
world comes from the Grabbit logo: a black field, a night-ink rabbit and wordmark
(#0e111a), and two violet pills (#6139f8) that glow. The demo runs in a dark event hall
and on a projector, so the page is dark only.

The surface is an Operate surface in the manner of a minimal AI chat. One centred column
holds the conversation. A report shows in that column as a short outline card, and the
full report opens in a side panel on the right, in the manner of an artifact panel.
"What changed" opens in the same panel. Below 64rem the panel covers the screen.

Decided on 2026-11-14 (#53); it replaces the cala.ai cream tone. Shipped code wins where
this file and the code differ.

**Key Characteristics:**
- Black ground, night-ink panels, near-white ink. Violet is light, never paint.
- One sans (Hanken Grotesk) for everything. Rank comes from weight and size.
- The agent speaks in plain text with no bubble. The user's lines sit in a dark pill.
- Flat surfaces separated by soft rules. Black shadows do not show on black, so lifted
  parts get a lighter edge, and the only glow is the violet light.

## Colors

### Primary
- **Violet** (#6139f8): the light. It glows under the composer, edges a new report
  outline and the alert toast, fills the "Rewritten for you" banner and the text
  selection, and colours the logo mark. Never use it for small text: it fails on black.
- **Violet light** (#a593ff): violet as text or as a line on black (the "Open report"
  link, the focus ring, the caret, warning badges, the "Live" dot). 7.6:1 on black.

### Neutral
- **Ground** (#000000): the page and the chat column.
- **Surface** (#0e111a): the logo's night ink. The side panel, the report outline card,
  cards.
- **Surface raised** (#161a26): the composer and the alert toast.
- **Panel strong** (#1d2230): user message pills, neutral badges, hover fills, skeleton
  bones.
- **Ink** (#f4f3fa): headings and primary buttons. **Text** (#d9d8e3): body.
  **Text muted** (#a3a2b2): meta, at any size. **Text faint** (#807f90): list markers and
  large text only.
- **Border** (#60657c): field and secondary button edges, 3.3:1 on black. **Border soft**
  (#262b3c): rules and card edges.

### Support
- **Info** (#9db4ff on #141b33): the Press trust badge.
- **Marker soft** (#1f1745): the violet wash on changed report parts and the chat change
  note.
- **Danger** (#ff8a7a on #2b1210): errors only.

### Named Rules
**The One Light Rule.** Violet means "the agent did something": it works, it changed the
report, it raised an alert. Never use it for decoration.

**The Trust Ladder Rule.** Trust strength reads from fill weight before hue: solid ink,
ink outline, blue tint, panel tint, dashed violet, dashed empty. A judge on a washed-out
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

## Layout

- **Top bar:** the violet two-pill mark and the "Grabbit" wordmark on the left, the live
  status next to it, then "Simulate event" (demo only), "What changed" and the "Demo
  data" badge on the right. No border.
- **Chat:** one column, 44rem max, centred while the panel is closed. Composer at the
  foot with suggestion chips above it.
- **Side panel:** `min(52rem, 56vw)` wide, surface fill, soft left edge, 14px top-left
  corner, sticky bar with the panel name and a close button. It slides in from 2rem right
  in 280ms. Escape and the close button close it, and focus returns to the opener. Below
  64rem it is fixed full screen.
- **Phone (375px):** the top bar wraps its actions to a second row; the panel covers the
  screen.

## Elevation & Depth

Flat by default. The side panel and cards sit on soft 1px edges. The large shadow pairs
a black drop with a 1px soft edge. The glow tokens (`--glow-rest`, `--glow-work`) fall
from below with a negative spread, like the logo's light, and only the composer, the
report outline and the alert toast carry them.

## Components

### Composer (signature)
A raised capsule, 24px corners, soft edge, resting violet glow below. The field inside has
no frame of its own. Focus turns the edge violet light. While the agent works, the edge
turns violet and the glow breathes between rest and full every 1.6s. Under reduced motion
it holds the full glow without motion. The send button is a round primary (ink) button.

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
Bottom right, raised surface, violet edge, large shadow plus the full glow, ink text,
"Open in chat" as a small ink pill. It stays until dismissed and uses `role="alert"`.

### Buttons
Pills. Primary: ink fill, black text. Secondary: border outline. Ghost: no fill, panel
strong on hover and when pressed (`aria-pressed`).

## Do's and Don'ts

### Do:
- **Do** take every value from `frontend/src/styles/tokens.css`.
- **Do** show a Trust Badge next to every fact, and "Not published" when Cala has no value.
- **Do** check every new text colour for 4.5:1 on black and on #0e111a.
- **Do** keep one primary (ink) button per view.

### Don't:
- **Don't** use violet (#6139f8) as text, or use any violet that is not the agent acting.
- **Don't** add a second typeface, gradients on text, or glass.
- **Don't** add a light theme.
- **Don't** put agent text in bubbles, or a report beside the chat before the user opens it.
- **Don't** use Cala's logo, wordmark or copy.
