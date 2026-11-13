# Filter results

> Narrow a web search by domain, recency, location, and language.

Write a natural-language query or use `site:`, `-site:`, `inurl:`, `intitle:`, quoted phrases, and `OR`.

## Search selected sites

Send this body to `POST /web/search`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "query": "API changelog",
  "includeDomains": [
    "stripe.com",
    "github.com"
  ],
  "freshness": "last_week",
  "numResults": 20
}
```

| Field | Limit or values |
| - | - |
| `query` | 1–500 characters. |
| `includeDomains` | Up to 100 domains. |
| `excludeDomains` | Up to 100 domains. |
| `freshness` | `last_24_hours`, `last_week`, `last_month`, or `last_year`. |
| `country` | Supported country code. |
| `languages` | A nonempty list of supported language codes, such as `["en", "de"]`, or `"all"` (default). |

Use `excludeDomains` to remove sources you do not want, such as social sites. More restrictive filters can yield fewer results than `numResults`.

Language filters support 74 languages. Results whose language cannot be detected remain eligible.

`queryFanout` is accepted for compatibility and currently has no effect. See [result content](https://docs.context.dev/search/page-content.md) to fetch the pages found by your query.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.