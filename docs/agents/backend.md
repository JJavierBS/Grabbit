# Backend

## Stack
- Language / framework: TODO
- Entry point: TODO
- Run: `make dev` (port TODO)

## Structure
TODO: where routes, business logic, data access and config live.

## Rules
- Handlers stay thin: parse and validate input, call a service, map the result.
- Validate all external input at the boundary. Trust nothing from the client.
- Errors follow the shape in api.md. Never leak stack traces or secrets in responses.
- Config only from environment variables; add every new one to `.env.example`.
- External calls (LLMs, third-party APIs) go through one wrapper per service, with timeout,
  so tests can mock them.
- Log events with context, never secrets or full personal data.
- Schema/data changes: TODO (migrations tool or seed script).
