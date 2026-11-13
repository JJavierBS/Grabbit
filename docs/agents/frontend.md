# Frontend

## Stack
- Framework: TODO
- Run: `make dev` (URL TODO)

## Structure
TODO: where pages/routes, components, API client and state live.

## Rules
- All server calls go through the single API client; components never call `fetch` directly.
- Types for API data come from the contract in api.md, not hand-written copies.
- Every view handles loading, empty and error states. The demo must never show a blank screen.
- Components: small, one responsibility, props typed. Reuse before creating.
- Styling follows styles.md. No inline magic colours or spacings.
- Use mocks from api.md when the backend endpoint is not ready yet.
