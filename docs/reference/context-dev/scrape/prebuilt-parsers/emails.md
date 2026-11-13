# Emails

> Extract and deduplicate contact email addresses from a page.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "emails"}`. Read the result in `parsed.data`, with `parsed.type: "emails"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use any supported page URL. The parser reads `mailto:` links, Cloudflare-obfuscated addresses, and visible text. It extracts from one page; it does not crawl linked pages.

```json theme={null}
{
  "url": "https://stripe.com/contact",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "emails"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface EmailsOutput {
  type: "emails";
  requested: true;
  success: true;
  data: {
    emails: { email: string }[];
  };
}
```

## Fields

```typescript theme={null}
interface Email {
  email: string;
}
```

Addresses are trimmed, converted to lowercase, validated, and deduplicated. Known placeholder domains and placeholder or unmonitored local parts are excluded. Hidden text and script contents are not scanned as visible text.

## Empty results and errors

No matching contact addresses produce `emails: []`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"emails"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser runs on page HTML after [content filtering](https://docs.context.dev/scrape/content-filtering.md). [Browser actions](https://docs.context.dev/scrape/browser-actions.md) can change the page before extraction, and [browser profiles](https://docs.context.dev/scrape/browser-profiles.md) can provide an authenticated session. Cached HTML can be reused; set `maxAgeMs: 0` for fresh data. [Timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md) and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) also apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.