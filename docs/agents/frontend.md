# Frontend

## Stack
- Framework: React 18 + TypeScript (strict) on Vite, npm. Server state with TanStack Query;
  no other state library. Alerts through `EventSource` on `/api/events` and the browser
  Notification API when the tab is hidden.
- Run: `make dev` (URL `http://localhost:5173`, proxies `/api` to `:8000`).
- Without a backend: `cd frontend && npm run dev:fake` serves the whole demo path from
  synthetic fixtures (`src/dev/fakeApi.ts`, `src/dev/fixtures.ts`). The "Alerts" button
  in the top bar fires a simulated alert 30 s after the click. Dev only; tests use `src/test/renderApp.tsx` (`mockApi`) instead.
- Design system reference: open `/?gallery`.
- Demo trigger: an "Alerts" button shows with the fake API, or with `?demo` (fixture
  `grei_seed_round`) or `?demo=<fixture>` against the real backend (`DEMO_MODE=1`).
- Guided demo (#184, `src/features/demo/`): a five-step tour on sample data for first-time
  visitors. It opens by itself on the first visit in a browser (`grabbit.demo.seen:v1`), and
  replays from "See how it works" on the empty chat, "How Grabbit works" at the
  sidebar foot, or `?tour`. `DemoRoot` swaps in a fresh `createDemoApi()` (a
  `createFakeApi` instance from `src/dev/fakeApi.ts`) and its own `QueryClient`, then
  restores both on exit. Inside it, `useDemo()?.active` is true: never write to the
  visitor's research, ask for permissions or call the real API from there. Every app
  control goes inside `<GuideLock>`, which disables it during the demo: the coach card makes
  every move. The one exception is the agent's question (#190): the visitor may pick an answer
  and send it by hand, as "Show me" would.

## Structure
- `src/api/`: generated `schema.ts` (api.md, `make gen-api`), named aliases in `types.ts`,
  the single `openapi-fetch` client in `client.ts` (`api.GET/POST` + `unwrap`), query hooks
  in `src/api/hooks/`. `setTransport` swaps the network for the fake API and the tests.
  `getUntyped` serves only `GET /api/reports` until #54 adds it to the schema.
- `src/features/chat/`, `src/features/report/`, `src/features/profile/`, `src/features/alerts/`:
  one folder per area, each with its components, hooks and tests.
- `src/components/`: shared pieces, e.g. `TrustBadge` (agent.md "Trust scale"), `FactValue`
  (value, date with its precision, "not published").
- `src/lib/`: pure helpers shared across features, e.g. `humanize` (readable words for
  Cala's stages, sectors and graph edges; never show a raw enum).
- `src/App.tsx`: layout. One screen: a centred chat; the report shows in the chat as an
  outline (`features/report/ReportOutline.tsx`) and opens in a side panel, which also holds
  "What changed". A left sidebar (`features/report/ReportSidebar.tsx`) lists every report;
  it collapses on wide screens and is a drawer on narrow ones. Alerts as toasts and desktop
  notifications.

## Rules
- All server calls go through the single API client; components never call `fetch` directly.
- Types for API data come from the contract in api.md, not hand-written copies.
- Every view handles loading, empty and error states. The demo must never show a blank screen.
- Components: small, one responsibility, props typed. Reuse before creating.
- Styling follows styles.md. No inline magic colours or spacings.
- Use mocks from api.md when the backend endpoint is not ready yet.
- Every `Fact` on screen shows its trust badge; a simulated alert shows "simulated event".
- Focus lives in the message box (#188, `features/chat/useComposerFocus.ts`): it takes focus
  when the chat opens, after each send and each reply, after Talk, on a stray keystroke and
  when the focused control disappears or turns disabled. A report opened from the sidebar or
  by a rewrite never takes it away on wide screens. Drafts are kept per research
  (`features/chat/draft.ts`). Never on touch screens or in the guided demo. Ctrl/Cmd+Shift+O
  starts a new research.
