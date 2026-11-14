---
name: Grabbit
description: A proactive research agent for business angels, in the warm, sourced tone of cala.ai.
colors:
  ground: "#f6e8cd"
  surface: "#fcf8f0"
  surface-raised: "#ffffff"
  panel: "#faefda"
  panel-strong: "#f1dfc0"
  ink: "#2e2723"
  text: "#39312c"
  text-muted: "#64574f"
  text-faint: "#7c6c63"
  on-ink: "#fcf8f0"
  border: "#968378"
  border-soft: "#d8c9c1"
  focus: "#075a8e"
  info: "#075a8e"
  info-bg: "#d6f0ff"
  marker: "#ffda7c"
  marker-soft: "#fee5b3"
  warning-ink: "#814d00"
  danger: "#a9241b"
  danger-bg: "#fbe4df"
typography:
  display:
    fontFamily: "Source Serif 4 Variable, Georgia, serif"
    fontSize: "2.5rem"
    fontWeight: 400
    lineHeight: 1.2
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Source Serif 4 Variable, Georgia, serif"
    fontSize: "1.875rem"
    fontWeight: 400
    lineHeight: 1.2
  lead:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 400
    lineHeight: 1.5
  body:
    fontFamily: "Hanken Grotesk Variable, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
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
  button-primary-hover:
    backgroundColor: "{colors.text}"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    padding: "8px 16px"
  button-secondary-hover:
    backgroundColor: "{colors.panel-strong}"
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
    padding: "20px"
  input:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "8px 12px"
  trust-filing:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.pill}"
  trust-primary:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
  trust-press:
    backgroundColor: "{colors.info-bg}"
    textColor: "{colors.info}"
    rounded: "{rounded.pill}"
  trust-aggregator:
    backgroundColor: "{colors.panel-strong}"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.pill}"
  trust-web-unverified:
    backgroundColor: "{colors.marker-soft}"
    textColor: "{colors.warning-ink}"
    rounded: "{rounded.pill}"
  trust-not-published:
    backgroundColor: "transparent"
    textColor: "{colors.text-muted}"
    rounded: "{rounded.pill}"
  toast-alert:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-ink}"
    rounded: "{rounded.lg}"
    padding: "16px"
---

# Design System: Grabbit

## Overview

**Creative North Star: "The annotated ledger"**

Grabbit lives on warm cream paper with brown-black ink, the tone the Cala team uses on
cala.ai. The brief pins that tone: Grabbit must feel at home at Cala's founders and
investors event. Grabbit keeps its own name and mark. It never uses Cala's logo, wordmark
or copy, and it never looks like a Cala product page.

The surface is an Operate surface: a chat beside a report. Calm paper and quiet borders
carry the structure. A serif names things (the report, a startup, a section). A plain sans
carries every fact, label and control. Colour is rare and has a job: it says how much to
trust a fact, or it marks what just changed.

Evidence: three cala.ai pages (home, finance industry, demos), captured on 2026-11-14 at
1440px and 375px with headless Chrome. Screenshots and computed styles live in
`material/design/cala/` (local, not committed).

**Voice, as observed on cala.ai.** Short declarative lines. The home page contrasts a
struck-out word with the true one (clutter, then clarity; scattered, then structured). Data
is described by its proof, not by hype: the finance page sums it up as "typed, sourced,
auditable, live." Sources are named concretely (registries, filings, sanctions lists).
Grabbit writes in the same register with its own words: say what changed and why in one
line, name the source, never inflate a signal into advice.

**Key Characteristics:**
- Cream ground (#f6e8cd), paper cards, brown-black ink. Light only: cala.ai ships no dark theme.
- Serif for names and titles, sans for everything a user reads to decide.
- Flat by default. Thin warm borders, not shadows, separate regions.
- Pills for actions, chips and badges. Soft 10px corners for cards and fields.
- Short, fast motion (150-280ms, standard ease). Nothing decorative.

## Colors

A warm, near-monochrome palette of beige paper and brown ink, with two measured accents:
an info blue and a marker yellow.

### Primary
- **Ink** (#2e2723): headings, primary buttons, the strongest trust badge, alert toasts.
  Measured as cala.ai's heading colour and primary button fill.

### Secondary
- **Info blue** (#075a8e on #d6f0ff): the press badge, links in focus, the focus ring. A
  darkened version of cala.ai's #006ba7 so that 12px text passes AA on its tint.

### Tertiary
- **Marker yellow** (#ffda7c, soft #fee5b3, ink #814d00): the "changed" highlight, the
  "web, unverified" badge and the "simulated event" label. Derived from cala.ai's accent
  yellow (#ffc234), lightened so ink text stays above 10:1 on it.

### Neutral
- **Ground** (#f6e8cd): the page. Measured as cala.ai's body background.
- **Surface** (#fcf8f0): cards and the report sheet. Measured.
- **Panel** (#faefda) and **panel strong** (#f1dfc0): the chat column and quiet chips.
  Derived from cala.ai's beige-100/200 roles, not measured directly.
- **Text** (#39312c): body copy, measured. **Text muted** (#64574f): secondary text at any
  size. **Text faint** (#7c6c63): cala.ai's muted colour; it reaches only 4.15:1 on the
  ground, so use it for text of 18px or more, or on the surface colour.
- **Border** (#968378) for fields and outlines, **border soft** (#d8c9c1) for card edges.
- **Danger** (#a9241b on #fbe4df): errors only. Cala's red (#e7000b) fails AA on cream.

### Named Rules
**The Trust Ladder Rule.** Trust strength reads from fill weight before hue: solid ink,
ink outline, blue tint, beige tint, dashed marker, dashed empty. A colour-blind judge on a
washed-out projector must still rank the six badges.

**The Marker Rule.** Yellow means "look here now": a fresh change, an unverified web hint
or a simulated event. Never use it for decoration.

## Typography

**Display Font:** Source Serif 4 (with Georgia)
**Body Font:** Hanken Grotesk (with system-ui)

**Character:** cala.ai sets headings in Tiempos (Klim, commercial) and text in Waldenburg
(commercial). Grabbit self-hosts the closest open faces: Source Serif 4 for the
calm, bookish serif and Hanken Grotesk for the neutral grotesk. Both ship with the app, so
the demo works offline.

### Hierarchy
- **Display** (400, 2.5rem, 1.2, -0.025em): the report title. Cala uses 60px on marketing
  pages; an app header needs less.
- **Title** (400 serif, 1.875rem, 1.2): section titles and startup names. Matches cala.ai's
  30px/36px h2.
- **Lead** (400, 1.25rem, 1.5): the report summary, one per screen.
- **Body** (400, 1rem, 1.5): chat messages and report prose, 65-75ch.
- **Small** (400, 0.875rem, 1.375): meta lines, field values, toast text.
- **Label** (500, 0.75rem, 1.5): badges, field hints, column labels. No uppercase eyebrows
  above headings.

### Named Rules
**The Name-and-Number Rule.** The serif names things; the sans states facts. A value, a
date or an amount is never set in the serif. All numerals are tabular.

## Layout

One screen. On a wide screen the chat column (26rem) sits beside the report, which reads as
a sheet of paper (max 60rem) centred on the cream ground, full width up to a 1920x1080 projector. Below
about 64rem the two stack, the report first, with the chat composer kept in reach. At 375px
there is a 16px gutter and no horizontal scroll.

Spacing runs on one 4px scale (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). cala.ai uses the same
steps: 20px card padding, 6-16px gaps, 48px section breaks. Groups are tight (8-12px);
sections are separated by 32-48px, with more space above a heading than below it.

## Elevation & Depth

Flat by default, as on cala.ai, where 98% of elements carry no shadow. Depth comes from
tone: the ground, the paper surface, and the panel colour. Shadows appear only on things
that float above the page.

### Shadow Vocabulary
- **Small** (`0 1px 3px rgb(46 39 35 / 0.1), 0 1px 2px -1px rgb(46 39 35 / 0.1)`): a
  hovered source link.
- **Medium** (`0 4px 6px -1px rgb(46 39 35 / 0.1), 0 2px 4px -2px rgb(46 39 35 / 0.1)`):
  menus and popovers.
- **Large** (`0 10px 15px -3px rgb(46 39 35 / 0.12), 0 4px 6px -4px rgb(46 39 35 / 0.12)`):
  toasts.

Shadows are brown-tinted, never pure black.

## Shapes

Two shapes only. Pills (999px) for everything you press or scan as a tag: buttons, chips,
badges. Soft rectangles for containers: 10px for cards and fields, 14px for toasts, 6px for
small inner pieces and the focus ring. Borders are 1px. Dashed borders carry meaning (the
weaker trust levels), never decoration.

## Components

### Buttons
- **Shape:** pill (999px).
- **Primary:** ink fill, cream text, 8px 16px, 14px medium. One per view.
- **Secondary:** transparent with a warm border; hover fills with panel strong.
- **Ghost:** text only; hover fills with panel strong.
- **States:** focus shows a 2px blue ring outside a cream gap; loading swaps the icon for a
  spinner and sets `aria-busy`; disabled drops to 55% opacity.

### Chips
- **Style:** the same pill as the Badge: 12px medium on a tint. cala.ai uses ink-filled
  pills for the selected filter and outlined pills for the rest; Grabbit follows that rule
  for any filter control.

### Cards / Containers
- **Corner Style:** 10px.
- **Background:** surface (#fcf8f0) on the ground.
- **Shadow Strategy:** none at rest (see Elevation).
- **Border:** 1px border soft.
- **Internal Padding:** 20px, or 24px 32px for the report sheet (20px below 40rem).
- Never nest cards. Inside a card, separate parts with space or a soft rule.

### Inputs / Fields
- **Style:** white field, 1px warm border, 10px corners, 8px 12px padding, 16px text.
- **Focus:** the border turns blue and the blue ring appears.
- **Error / Disabled:** error turns the border red and shows a red message linked by
  `aria-describedby`; disabled uses the panel colour.

### Navigation
None. Grabbit is one screen; the profile history opens in place, not on a new page.

### Trust Badge (signature component)
Six pills, one per `TrustLevel` (agent.md "Trust scale"), each with a Lucide icon and the
label from agent.md: Official filing (solid ink, landmark), Company or investor (ink
outline, building), Press (blue tint, newspaper), Database (beige tint, database), Web,
unverified (dashed marker, globe), Not published (dashed empty, dashed circle). With a
source URL the badge is a link that opens the source in a new tab. A compact form hides the
text but keeps it in the accessible name.

### Changed Highlight (signature moment)
When the report rewrites itself after a correction, every part that changed carries a
marker-yellow wash and a short "Changed" label for about four seconds, then fades in
280ms. Removed startups leave a struck-through line for the same time. With reduced motion
the marks stay without animation.

### Simulated Event Label
A warning badge (marker soft, dark amber text, 1px amber border) that reads "Simulated
event". It sits on the toast, the notification text and the alert in the chat whenever
`simulated=true`.

### Toast
Bottom-right, 24rem wide (full width minus 16px at 375px). Default toasts are paper cards
with a large shadow and close after 8s. Alert toasts are ink with cream text, stay until
dismissed, and use `role="alert"`.

## Do's and Don'ts

### Do:
- **Do** take every colour, size, radius, shadow and duration from
  `frontend/src/styles/tokens.css`.
- **Do** show a Trust Badge next to every fact, and "Not published" when Cala has no value.
- **Do** keep one primary (ink) button per view.
- **Do** keep motion between 150ms and 280ms, on state changes only.
- **Do** check every new text colour against the ground (#f6e8cd) for 4.5:1.

### Don't:
- **Don't** use Cala's logo, wordmark, hero lines or brush-stroke strike-throughs.
- **Don't** use cala.ai's muted brown (#7c6c63) for small text on the ground.
- **Don't** set numbers, dates or amounts in the serif.
- **Don't** add a dark theme, gradients, glass or pure-black shadows.
- **Don't** put an uppercase eyebrow label above a heading.
