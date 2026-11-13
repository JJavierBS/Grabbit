# Freshness and caching

> Choose when to reuse an output and when to fetch a fresh page.

`maxAgeMs` controls how old a cached output may be. It defaults to three days (`259200000` milliseconds) and accepts up to one year of 365 days (`31536000000` milliseconds). Set `0` for a fresh capture. Values must be whole milliseconds between zero and the maximum; values outside that range are rejected.

## Fetch a fresh page

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true,
    "screenshot": true
  },
  "maxAgeMs": 0
}
```

## Independent outputs

Each output is cached separately. One response can combine outputs captured on different visits within `maxAgeMs`; request them together with `maxAgeMs: 0` when they must reflect the same visit. Changing a screenshot option need not refetch compatible Markdown.

Requests with custom headers, browser actions, or ZDR bypass the shared cache. Hosted image files refresh after 23 hours so their links remain usable.

## Read cache metadata

| Field | Meaning |
| - | - |
| `cache_metadata.status` | `hit`, `miss`, or `zdr`. A composite response is a hit only when all contributing cached fetches were hits. |
| `cache_metadata.age_ms` | Age of the oldest contributing cached data; `0` for a miss or ZDR. |

For slower-changing pages, use `maxAgeMs: 604800000` to accept a week-old result. Failed retrievals and incomplete captures are not cached as complete outputs. Valid pieces may still be cached independently, including pieces omitted because the full response exceeded its size limit.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.