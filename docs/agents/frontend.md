# Frontend

## Stack
- Framework: React 18 + TypeScript (strict) on Vite, npm. Server state with TanStack Query;
  no other state library. Alerts through `EventSource` on `/api/events` and the browser
  Notification API when the tab is hidden.
- Run: `make dev` (URL `http://localhost:5173`, proxies `/api` to `:8000`).

## Structure
- `src/api/`: generated `schema.ts` (api.md), the single client `client.ts`, query hooks.
- `src/features/chat/`, `src/features/report/`, `src/features/alerts/`: one folder per area,
  each with its components, hooks and tests.
- `src/components/`: shared pieces, e.g. `TrustBadge` (agent.md "Trust scale"), `FactValue`
  (value, date with its precision, "not published").
- `src/App.tsx`: layout. One screen: chat beside the current report; alerts as toasts and
  desktop notifications.

## Rules
- All server calls go through the single API client; components never call `fetch` directly.
- Types for API data come from the contract in api.md, not hand-written copies.
- Every view handles loading, empty and error states. The demo must never show a blank screen.
- Components: small, one responsibility, props typed. Reuse before creating.
- Styling follows styles.md. No inline magic colours or spacings.
- Use mocks from api.md when the backend endpoint is not ready yet.
- Every `Fact` on screen shows its trust badge; a simulated alert shows "simulated event".
