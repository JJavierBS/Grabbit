# Styles

## Design system
- Library / CSS approach: plain CSS Modules (`Name.module.css` next to `Name.tsx`), no UI
  kit. Icons from `lucide-react`. Fonts self-hosted with `@fontsource-variable` (Source
  Serif 4 for names and titles, Hanken Grotesk for everything else), so the demo works
  offline.
- Tokens file: `frontend/src/styles/tokens.css` (colours, spacing, radius, typography,
  shadows, motion live there, nowhere else). Global element styles: `src/styles/base.css`.
- Brand: the visual tone of cala.ai (cream ground, brown ink, serif titles), measured and
  explained in `DESIGN.md`. Grabbit keeps its own name and mark: never Cala's logo,
  wordmark or copy. Product context for design work: `PRODUCT.md`.
- Base components in `frontend/src/components/`: `Button`, `Card`, `Badge`, `TrustBadge`,
  `Input` / `TextArea`, `Toast` (`ToastProvider`, `useToast`), `Skeleton`. Reuse them
  before you write a new one. A visual reference renders from `src/design/Gallery.tsx`.
- Shared recipes in `src/styles/shared.module.css` (`display` and `title` serif headings, the
  paper `sheet`); use them with `composes:` instead of copying the declarations.
- Accessibility check: axe-core reports no violations on the report, history, alert and
  gallery at 1920x1080 and 375px (2026-11-14). Keep it that way.
- Light theme only: cala.ai has no dark theme.

## Rules
- Use tokens, never raw hex values or pixel spacings in components.
- Spacing on one scale (e.g. 4/8/12/16/24/32).
- Text contrast at least WCAG AA. Interactive elements have visible focus states.
- Layout works at 375px wide and at projector resolution (1920x1080): the demo is projected.
- Prefer one clear primary action per screen; judges see it for seconds.
- Motion only when it explains a state change; keep it under 300ms.
