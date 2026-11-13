# Page content

> Choose how each crawled page becomes Markdown.

Crawl options live at the top level of the request. Their names differ from Scrape: use `useMainContentOnly` and `waitForMs`, not Scrape’s `sharedParams` fields. Unknown Crawl fields can be ignored, so check names carefully.

## Keep article content

Send this body to `POST /web/crawl`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com/blog",
  "maxPages": 10,
  "useMainContentOnly": true,
  "excludeSelectors": [
    "nav",
    "footer"
  ],
  "includeLinks": true,
  "includeImages": false
}
```

| Field | Default | Effect |
| - | - | - |
| `useMainContentOnly` | `false` | Remove detected page chrome. |
| `includeSelectors`, `excludeSelectors` | None | Keep or remove matching elements; exclusions win. |
| `sourcePreference` | `["html-conversion", "markdown-direct"]` | Convert page HTML or use the Markdown a page publishes, in order of preference; see [Choose the Markdown source](https://docs.context.dev/scrape/markdown.md#choose-the-markdown-source). |
| `includeLinks` | `true` | Keep link destinations. Requires `html-conversion` in `sourcePreference`. |
| `includeImages` | `false` | Include image references. Requires `html-conversion` in `sourcePreference`. |
| `shortenBase64Images` | `true` | Replace inline base64 payloads with placeholders. Requires `html-conversion` in `sourcePreference`. |
| `includeFrames` | `false` | Read iframe content. |
| `waitForMs` | 3,500 | Wait before extraction. |
| `settleAnimations` | `false` | Wait for CSS animations. |
| `maxAgeMs` | One day | Accept cached page content; `0` fetches fresh. |

Use `pdf: {"shouldParse":true,"ocr":true,"start":1,"end":5}` for selected PDF pages. Page numbers are inclusive and start at 1. OCR recovers scanned pages while preserving existing text.

`country` selects the fetch location, `zdr` applies [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), and `tags` label the request in [usage logs](https://docs.context.dev/optimization/usage-and-logs.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.