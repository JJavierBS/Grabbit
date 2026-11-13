# Comments

- Prefer self-describing names over comments.
- Comment only a why the code cannot express: a non-obvious decision, a workaround, an
  external limitation. Link the source (issue, docs URL) when there is one.
- Never restate the code, never narrate the change ("added for...", "now uses...").
- No emojis, no decorative separators, no commented-out code, no TODO without an issue number
  (`TODO(#23): ...`).
- Docstrings only on public functions/components whose contract is not obvious from the
  signature. Style: TODO (JSDoc / Google-style docstrings / ... once the stack is chosen).
- English, short, one line when possible.
