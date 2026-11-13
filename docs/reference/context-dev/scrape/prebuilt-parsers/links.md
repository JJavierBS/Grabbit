# Links

> Extract absolute HTTP and HTTPS links with their text labels.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "links"}`. Read the result in `parsed.data`, with `parsed.type: "links"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use any supported page URL. The parser reads anchors with an `href` on that page; it does not crawl destinations. For site-wide URL discovery, use [Map URLs](https://docs.context.dev/map/overview).

```json theme={null}
{
  "url": "https://context.dev",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "links"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface LinksOutput {
  type: "links";
  requested: true;
  success: true;
  data: {
    links: Link[];
  };
}
```

## Fields

```typescript theme={null}
interface Link {
  url: string;
  text: string | null;
}
```

Relative URLs resolve against the document base URL, including a valid `<base href>`, or the final page URL. Only HTTP and HTTPS URLs are returned; fragment-only references, `mailto:`, `tel:`, and JavaScript links are excluded.

Links are deduplicated by their resolved URL. The first non-empty label wins: visible text is preferred within an anchor, then `aria-label`, then image `alt` text. Missing labels are `null`. Hidden anchors can still contribute a URL with `text: null`; anchors inside templates are excluded.

## Empty results and errors

No matching links produce `links: []`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"links"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser runs on page HTML after [content filtering](https://docs.context.dev/scrape/content-filtering.md). [Browser actions](https://docs.context.dev/scrape/browser-actions.md) can change the page before extraction, and [browser profiles](https://docs.context.dev/scrape/browser-profiles.md) can provide an authenticated session. Cached HTML can be reused; set `maxAgeMs: 0` for fresh data. [Timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md) and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) also apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.