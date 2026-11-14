# Styles

## Design system
- Library / CSS approach: plain CSS Modules (`Name.module.css` next to `Name.tsx`), no UI
  kit. Icons from `lucide-react`. Hanken Grotesk for all text, and Outfit for
  the logo wordmark only, both self-hosted with `@fontsource-variable`, so the demo works
  offline.
- Tokens file: `frontend/src/styles/tokens.css` (colours, spacing, radius, typography,
  shadows, motion live there, nowhere else). Global element styles: `src/styles/base.css`.
- Brand: "Afterglow", taken from the Grabbit logo: near-white ground, white panels,
  night-ink text, one violet light (#6139f8). Explained in `DESIGN.md`. Grabbit keeps its own name and mark:
  never Cala's logo, wordmark or copy. Product context for design work: `PRODUCT.md`.
- Base components in `frontend/src/components/`: `Button`, `Card`, `Badge`, `TrustBadge`,
  `Input` / `TextArea`, `Toast` (`ToastProvider`, `useToast`), `Skeleton`. Reuse them
  before you write a new one. A visual reference renders from `src/design/Gallery.tsx`.
- Shared recipes in `src/styles/shared.module.css` (`display` and `title` headings, the
  `sheet` content column of the side panel); use them with `composes:` instead of copying the declarations.
- Accessibility check: axe-core reports no violations on the report, history, alert and
  gallery at 1920x1080 and 375px (2026-11-14). Keep it that way.
- Light theme only: the team asked for a lighter page on 2026-11-14 (#53).

## Rules
- Use tokens, never raw hex values or pixel spacings in components.
- Spacing on one scale (e.g. 4/8/12/16/24/32).
- Text contrast at least WCAG AA. Interactive elements have visible focus states.
- Layout works at 375px wide and at projector resolution (1920x1080): the demo is projected.
- Prefer one clear primary action per screen; judges see it for seconds.
- Motion only when it explains a state change; keep it under 300ms. Two exceptions are
  states, not transitions: the composer glow breathes while the agent works or listens, and a new
  report outline lands with light that fades in 1.2s. Both stop under reduced motion.
