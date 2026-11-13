# Submit a batch

> Submit URL lists with extraction options and safe retry keys.

Submit 1–100,000 URL records to `POST /batch/submit`. Use the [Batches overview](https://docs.context.dev/batches/overview#submit-a-url-list) for runnable SDK examples, or [Large crawls](https://docs.context.dev/crawl/async.md) for discovery from a site.

## URL records and formats

```json theme={null}
{
  "input": {
    "mode": "scrape",
    "data": {
      "formats": { "markdown": true, "html": true },
      "urls": [
        {
          "url": "https://example.com/about",
          "itemId": "about",
          "meta": {
            "section": "company"
          }
        }
      ],
      "sharedParams": {
        "mainContentOnly": true
      }
    }
  },
  "tags": [
    "site-import"
  ],
  "policies": [
    "pol_3f9c2a7e5b8d4c1f9a6e0b2d7c4f8a1e"
  ]
}
```

`itemId` and `meta` are returned with each page. Duplicate URLs are deduplicated; rejected URLs appear in `invalid_urls` (up to 100 entries), each with a `reason` such as `Must be a public http:// or https:// URL`. Keep the request body within 24 MiB and use public HTTP(S) URLs.

Set at least one output in `formats` to `true`: `markdown`, `html`, `screenshot`, `images`, `bytes`, `parse`, `product`, `highlights`, or `json`. Combine outputs in one request. Every page uses the same options as [Scrape Anything](https://docs.context.dev/scrape/overview), with `urls` replacing the single `url`.

## Per-page options

| `input.data` field | Default or behavior |
| - | - |
| `sharedParams` | Browser actions, custom headers, profiles, content filters, country, viewport, waits, and PDF parsing. Uses the same defaults as Scrape Anything. |
| `markdownParams`, `screenshotParams`, `imageParams`, `productParams` | Options for the corresponding requested output. |
| `parseParams` | Required for `formats.parse`; custom rules or a supported prebuilt parser. |
| `jsonParams` | Required for `formats.json`; provide a JSON schema. |
| `highlightsParams` | Required for `formats.highlights`; provide a query. |
| `maxAgeMs` | Three days (`259200000` ms), maximum 365 days (`31536000000` ms); `0` fetches fresh. Applies to both scrape and crawl batches. |
| `timeoutOpts` | Deadline for each page. Defaults to 90,000 ms with `fail`; up to 300,000 ms. `return-partial` preserves completed outputs. |
| `zdr` | Batches retain result files, so only `disabled` is supported. `enabled` returns `ZDR_NOT_SUPPORTED`. |

Use up to 20 request tags. Configure `webhook: {"url":"https://app.example.com/hooks/context","retry":{}}` for [signed completion events](https://docs.context.dev/webhooks.md); do not send `webhookUrl` at the same time. The response then includes `webhook_secret`, which is returned only there. Save it immediately in [server-side secret storage](https://docs.context.dev/webhooks.md#store-the-signing-secret), associated with the batch `id`, and use it to [verify incoming deliveries](https://docs.context.dev/webhooks.md#verify-signatures).

`policies` lists [access policy](https://docs.context.dev/optimization/access-policies.md) IDs to apply to every page. A URL must pass every policy; blocked URLs are listed in `invalid_urls` and never run.

Credits follow Scrape Anything pricing for each page. The selected outputs reserve the maximum page cost at submission; unused extraction credits and unattempted pages are refunded at settlement. OCR is charged separately for recovered pages. A partial result is successful when at least one requested output succeeds.

## Idempotency

Send an `Idempotency-Key` header, up to 200 characters, unique within your organization. Retrying the same key and body returns the original batch; a different body returns 409. Keep the key and payload together when retrying an uncertain submission.

## Recover selected pages

Read [result records](https://docs.context.dev/batches/results.md#read-results), select failed URLs, and submit them as a new batch with a new idempotency key. Use `maxAgeMs: 0` for a fresh price list, or remove it when recent cached pages are acceptable. Check [limits and errors](https://docs.context.dev/batches/limits-and-errors.md) before increasing concurrency.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.