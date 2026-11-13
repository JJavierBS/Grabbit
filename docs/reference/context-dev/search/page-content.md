# Result content

> Read Markdown or highlights with search results and handle each page’s outcome.

Set `markdownOptions.enabled` to `true` to return each result’s page as Markdown, or `highlightsOptions.enabled` to return only the passages relevant to your query. A search result can remain useful even when its page content cannot be read.

## Request page content

Send this body to `POST /web/search`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "query": "Stripe API authentication",
  "markdownOptions": {
    "enabled": true,
    "useMainContentOnly": true,
    "includeLinks": true
  }
}
```

## Request highlights

Highlights use the search `query` and read each page with the `markdownOptions` settings, so you can request them without Markdown.

```json theme={null}
{
  "query": "Stripe API authentication",
  "highlightsOptions": {
    "enabled": true,
    "maxCharacters": 1500
  }
}
```

Each result’s `highlights.highlights` lists passages in page order. See [Highlights](https://docs.context.dev/scrape/highlights.md) for the passage format.

## Read each outcome

Check the result’s `markdown.code` and `highlights.code` before using their content:

| Code | Meaning |
| - | - |
| `SUCCESS` | Page content is available. |
| `NOT_REQUESTED` | The output was not enabled. |
| `TIMEOUT` | The page exceeded its deadline. |
| `CONTENT_TOO_LARGE` | The page exceeded the content limit. |
| `WEBSITE_ACCESS_ERROR` | The page could not be accessed. |
| `WEBSITE_BLOCKED` | The site served an anti-bot challenge or access wall. |
| `ERROR` | Another extraction failure. |

Each result’s `markdown.finalDOMState` is `loaded`, or `still-loading` when capture ended before the page finished loading. Highlights can succeed with an empty array when no passage is relevant.

## Options

`markdownOptions` supports `includeLinks` (default true), `includeImages` (false), `shortenBase64Images` (true), `useMainContentOnly` (false), `includeFrames` (false), and `maxAgeMs` (180 days, or 365 days when only highlights are requested). `maxAgeMs` accepts at most 365 days (31,536,000,000 ms); `0` forces a fresh scrape. `highlightsOptions.maxCharacters` (default 4,000; 100–20,000) limits the combined passage length per result.

`markdownOptions.pdf` controls PDF results. `shouldParse` (default true) parses PDF URLs; when false, PDF results are skipped with `WEBSITE_ACCESS_ERROR`. `start` and `end` limit parsing to an inclusive, 1-based page range: `end` defaults to the final page and must be at least `start`.

`waitForMs` accepts 0–30,000 ms. Each page read has a default deadline of 20 seconds plus any `waitForMs`; set `markdownOptions.timeoutOpts` to change it. Its `milliseconds` (1–300,000) is required, and `behavior` is `fail` (default) or `return-partial`, which returns the available results and requires at least 5,000 ms. Top-level `timeoutOpts` limits the whole search.

Markdown and highlights add charges; see [Credits and pricing](https://docs.context.dev/account/credits.md).

Keep the URL, title, and description when a content read fails. For page-specific recovery, call [Scrape](https://docs.context.dev/scrape/overview) with appropriate waits or filters.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.