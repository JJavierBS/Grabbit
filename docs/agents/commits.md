# Commits and PR titles

`[<user>] [<TYPE>] (#<issue>) <Summary>`

- `<user>`: the GitHub username of the person driving the work (`gh api user --jq .login`).
- `<TYPE>`: uppercase. `FEATURE`, `FIX`, `DOCS`, `REFACTOR`, `TEST`, `STYLE`, `CHORE`,
  `BUILD`, or another one the developer asks for.
- `(#<issue>)`: the issue the branch belongs to. Branches are `<issue>-<slug>`, so take the
  number from the branch name. Omit it only when there is no issue.
- Summary: English, imperative mood, capitalised, no period. Whole line max 72 characters.
- Breaking change to a shared contract: add `!` after the type (`[FEATURE!]`).
- Body only when it explains a non-obvious why. Wrap at 72.
- No trailers, no emojis, no tool attribution (no `Co-Authored-By` for assistants, no
  "Generated with").
- The `commit-msg` hook rejects messages that do not follow this format. Merge and revert
  commits made by git are let through.
- PRs are squash-merged: the PR title is the commit that lands on main, so it follows the
  same format. Also put `Closes #<issue>` in the PR body so the issue closes on merge.

Examples:
- `[JJavierBS] [FEATURE] (#12) Add Cala API wrapper with response cache`
- `[JJavierBS] [FIX] (#9) Retry Cala queries on 429`
- `[JJavierBS] [DOCS] (#3) Fill architecture overview`
- `[JJavierBS] [CHORE] Bootstrap repository` (no issue)
