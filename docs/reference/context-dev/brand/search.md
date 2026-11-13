# Auto-complete Brand

> Find up to ten brand candidates by company name or domain.

Use `GET /brand/search` for autocomplete. Results contain `domain`, `name`, and `logo`, plus `description`, `country`, and `language` when available; use the chosen domain with [Retrieve a brand](https://docs.context.dev/brand/lookup-by-domain.md) for a full profile.

## Search query

Set `query=stri` to find candidates such as Stripe. The query is required and accepts 1–100 characters. See the [reference](https://docs.context.dev/api-reference/brand-intelligence/search.md) for a runnable request.

| Parameter | Default | Effect |
| - | - | - |
| `country` | None | Match an uppercase ISO country code, such as `US` or `GB`. |
| `language` | None | Match a supported primary language, such as `english` or `french`. |
| `autocomplete` | `true` | Prefix matching for partially typed queries. |
| `queryBy` | Name and domain | Search `name`, `domain`, or both. |
| `typoTolerance` | 0 | Allow up to two typos. |
| `tags` | None | Label request usage. |

For example, `query=stri&country=US&language=english` requires both filters to match. Returned `country` and `language` values can be reused as exact filters; `description` is not searchable or filterable.

Debounce typed input and cancel superseded UI updates. The API returns at most ten results: name matches first, then domain matches, with the most popular brands first within each group. Let the user choose a candidate.

## Display a result logo

`logo` is a [Logo Link](https://docs.context.dev/brand/logo-link.md) URL for your organization. It can be an empty string if no public client ID exists. Image loads use Logo Link’s quota and referring-domain restrictions, so handle unavailable images in the UI.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.