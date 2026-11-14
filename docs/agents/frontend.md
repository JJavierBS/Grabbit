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
- Demo trigger: a "Simulate event" button shows with the fake API, or with `?demo` (fixture
  `new_round`) or `?demo=<fixture>` against the real backend (`DEMO_MODE=1`).

## Structure
- `src/api/`: generated `schema.ts` (api.md, `make gen-api`), named aliases in `types.ts`,
  the single `openapi-fetch` client in `client.ts` (`api.GET/POST` + `unwrap`), query hooks
  in `src/api/hooks/`. `setTransport` swaps the network for the fake API and the tests.
  `getUntyped` serves only `GET /api/reports` until #54 adds it to the schema.
- `src/features/chat/`, `src/features/report/`, `src/features/profile/`, `src/features/alerts/`:
  one folder per area, each with its components, hooks and tests.
- `src/components/`: shared pieces, e.g. `TrustBadge` (agent.md "Trust scale"), `FactValue`
  (value, date with its precision, "not published").
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
