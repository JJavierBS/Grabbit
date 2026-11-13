# Lookup by page URL

> Extract brand details from one exact page.

Use `type: "by_direct_url"` to inspect one public HTTP(S) page. Results are limited to that page; domain resolution and cross-site enrichment do not run.

## Request

Send this body to `POST /brand/retrieve`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "type": "by_direct_url",
  "direct_url": "https://stripe.com/about"
}
```

This lookup accepts `timeoutOpts`, `tags`, `policies`, and `zdr`. It does not accept cache, speed, or language controls used by the other lookup types.

## Sparse pages and failures

A page with little branding can return a sparse profile. Choose [lookup by domain](https://docs.context.dev/brand/lookup-by-domain.md) when you want the company’s broader profile.

Handle `WEBSITE_ACCESS_ERROR`, `WEBSITE_BLOCKED`, and `WEBSITE_NOT_FOUND` as target-specific failures. Keep the submitted URL and `request_id` when investigating the result.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.