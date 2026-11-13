# Location and headers

> Choose a fetch country and send headers to the target site.

Set `sharedParams.country` for a country-specific fetch. `sharedParams.headers` sends HTTP headers to the target site and bypasses caching.

## Fetch a localized page

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true
  },
  "sharedParams": {
    "country": "DE",
    "headers": {
      "Accept-Language": "de-DE,de;q=0.9"
    }
  }
}
```

## Country

Use a supported two-letter ISO 3166-1 code. Codes are case-insensitive and apply to page fetches and image downloads. An unsupported code returns 400; the [reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) lists accepted values.

## Target headers

Send at most 50 headers. Names must be unique and at most 256 characters; values at most 8,192 characters with no line breaks. Host, Content-Length, and transport headers such as Connection and Transfer-Encoding are rejected.

Use `Referer` for an image that requires a referring page. Use `Cookie` or `Authorization` only for a target you are authorized to access. Your Context.dev API key belongs in the request’s Authorization header, outside `sharedParams`.

Credentials are stripped when a redirect changes origin. A blocked target can return failed outputs in HTTP 200; a restricted domain can return `403 FORBIDDEN`. See [error handling](https://docs.context.dev/scrape/timeouts-and-errors.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.