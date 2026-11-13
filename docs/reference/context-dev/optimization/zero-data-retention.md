# Zero data retention

> Choose per-request retention controls for web content, brand retrieval, and styleguides.

Zero data retention (ZDR) is an organization entitlement requested per call. Contact [support@context.dev](mailto:support@context.dev) to enable it before using `zdr: "enabled"`.

## Supported endpoints

| Endpoint | Send `zdr` in |
| - | - |
| Scrape, Crawl, Search, Answers, People Enrich, People Search, Company Search | JSON body. |
| Brand retrieval, all lookup types | JSON body. |
| Map URLs, Styleguide | Query string. |
| Parse | Query string beside upload options. |

Batches, Monitors, and feedback do not support this request mode. Unsupported routes reject it with `ZDR_NOT_SUPPORTED`.

## Enable a request

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true
  },
  "zdr": "enabled"
}
```

For query-based endpoints, add `zdr=enabled`. Omitted or `disabled` uses standard mode. Invalid values, both locations, or the wrong location return `400 INPUT_VALIDATION_ERROR`.

## Confirm ZDR was honored

Successful supported responses, including Scrape, include `X-Context-ZDR: true`. Scrape also returns `cache_metadata.status: "zdr"` and `age_ms: 0`. Verify the confirmation before recording that the control was applied.

## What changes

### Brand retrieval and Styleguide

For [Brand retrieval](https://docs.context.dev/brand/overview) and [Styleguide](https://docs.context.dev/brand/styleguide.md), `zdr: "enabled"` suppresses application logs, request-log entries, and exported traces. Brand records, shared caches, and hosted assets can still be read and saved. This mode does not make brand data ephemeral. Cloudflare platform invocation logging is unchanged.

Send this body to `POST /brand/retrieve`:

```json theme={null}
{
  "type": "by_domain",
  "domain": "example.com",
  "zdr": "enabled"
}
```

For Styleguide, add `zdr=enabled` to the query string. Both require the organization's ZDR entitlement and confirm acceptance with `X-Context-ZDR: true`. Cache metadata can still report `hit` or `miss`. These requests do not appear in request-log history. Fresh `maxSpeed` Brand results skip background refresh and are not saved as shared brand records.

### Other supported endpoints

Shared caches and asset uploads are skipped. Retained logs contain operational metadata without request/response bodies, query values, user agent, or tags. Uploaded bytes and screenshots are processed in memory. AI processing uses a dedicated zero-retention configuration.

| Feature | Under ZDR |
| - | - |
| Scrape screenshots | Inline image data URLs remain available. |
| Scrape images | Original URLs remain; hosted `fileUrl` is omitted. |
| Map | URLs without shared page metadata or background enrichment. |
| People | Hosted `avatar_url` is omitted. |
| PDF OCR | Skipped. |

These requests may take longer without shared cache reuse. Your application remains responsible for its own content storage and logs.

A `403 ZDR_NOT_ENABLED` means the organization lacks the entitlement. See [security and trust](https://docs.context.dev/optimization/trust.md) and the [DPA](https://context.dev/dpa) for broader data-handling requirements.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.