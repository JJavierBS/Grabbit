# Testing

Goal: four people and many agents change the same code fast. Tests are how we notice when
an agent breaks something that already worked. `make test` is the single entry point and
will be what CI/CD runs, so everything must pass through it alone, from a clean clone.

## Required
- Every feature ships with tests that pin its behaviour: if another change breaks it later,
  a test must fail. Cover the happy path plus the edge cases from the acceptance criteria.
- Every bug fix starts with a test that reproduces the bug and fails before the fix.
- Test behaviour through public interfaces (API responses, rendered output, function
  results), not internals, so refactors do not break tests for no reason.
- Never delete, skip or loosen an existing test to make your change pass. If the behaviour
  is meant to change, say so explicitly in the PR description.
- The PR template asks which tests protect the change: answer concretely.

## Keep tests cheap
- No real network or paid APIs in tests: mock external services at their wrapper.
- Deterministic: fixed seeds, fixed clock, no ordering assumptions.
- `make test` stays under ~60 s and prints only failures and a summary.

## Layout
- Framework: backend pytest (+ pytest-asyncio, respx to mock httpx); frontend Vitest +
  Testing Library (jsdom). `make test` runs both quietly (`pytest -q`, Vitest dot reporter).
- Location and naming: `backend/tests/test_<module>.py`, mirroring `app/`;
  `frontend/src/**/<Name>.test.tsx` next to the component.
- Fixtures / seed data: recorded Cala responses in `backend/tests/fixtures/cala/` (real
  shapes, trimmed); Gemini never runs in tests, use `FakeLLM` with scripted replies; API
  fixtures in `backend/app/fixtures/` feed both the mock endpoints and frontend tests.
  Freeze time with an injected clock, not the system clock.
- Must-have tests: Cala normalisation to `Fact` (both `document` shapes, absent ->
  `not_published`), each signal function, profile changes and undo, watcher diff, and the
  trust badge rendering.
