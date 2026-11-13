# Scope and limits

> Bound a crawl by page count, path, depth, and time.

Crawl starts at `url` and follows eligible links. Send these fields to `POST /web/crawl`.

## Limit a crawl

Send this body to `POST /web/crawl`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/docs",
  "maxPages": 50,
  "maxDepth": 2,
  "urlRegex": "^https://example[.]com/docs/",
  "stopAfterMs": 60000
}
```

| Field | Default | Limit |
| - | - | - |
| `maxPages` | 100 | 1–500 pages. |
| `maxDepth` | Unset | Limit link depth from the start URL. |
| `urlRegex` | None | RE2-compatible URL filter, up to 256 characters. |
| `excludeUrlRegex` | None | RE2-compatible pattern for URLs to skip, up to 256 characters. Wins over `urlRegex`; the start URL is always crawled. |
| `followSubdomains` | `false` | Permit child hosts. |
| `stopAfterMs` | 80,000 | Soft budget of at least 10,000 ms. Values above 110,000 are capped at 110,000. |
| `timeoutOpts` | Unset | Request deadline; minimum 1,000 ms. |

The soft budget is checked after each page finishes, so it can be exceeded by the current page. `timeoutOpts` sets the overall deadline; choose `return-partial` when completed pages are useful.

A page cap is a maximum, not a promise: a site may expose fewer eligible links. For more than 500 pages, use [Large crawls](https://docs.context.dev/crawl/async.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.