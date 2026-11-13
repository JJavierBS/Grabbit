# API contract

Contract first: change the contract, then the backend and frontend. This lets both sides
work in parallel against mocks.

- Source of truth: TODO (e.g. `api/openapi.yaml` or shared types in `packages/types`)
- Mocks: TODO (where they live, how the frontend switches to them)
- Base URL: TODO (local and deployed)

## Rules
- A PR changing the contract updates contract, mocks and both sides' types together, or
  opens issues for the side it does not touch.
- Breaking changes use `!` in the PR title and are announced in the team chat.
- Error shape for every endpoint: `{ "error": { "code": "snake_case", "message": "..." } }`
  with a matching HTTP status.
- Names: TODO (camelCase or snake_case in JSON; pick one).

## Endpoints
| Method | Path | Purpose | Status |
| --- | --- | --- | --- |
| TODO | | | mock / real |
