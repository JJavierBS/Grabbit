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
- Framework: TODO
- Location and naming: TODO
- Fixtures / seed data: TODO
