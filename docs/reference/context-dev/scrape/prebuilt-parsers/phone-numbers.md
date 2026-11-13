# Phone numbers

> Extract valid phone numbers and return deduplicated international numbers.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "phone-numbers"}`. Read the result in `parsed.data`, with `parsed.type: "phone-numbers"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use any supported page URL. The parser reads `tel:` links and visible text on that page; it does not crawl linked pages.

```json theme={null}
{
  "url": "https://stripe.com/contact",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "phone-numbers"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface PhoneNumbersOutput {
  type: "phone-numbers";
  requested: true;
  success: true;
  data: {
    phone_numbers: { phone: string }[];
  };
}
```

## Fields

```typescript theme={null}
interface PhoneNumber {
  phone: string;
}
```

Valid numbers are normalized to E.164 format, such as `+14155552671`, and deduplicated. Extensions are not included in the returned value. National numbers use the region in the page’s HTML `lang` attribute, then a supported country-code domain, then `US`. Globally used domain suffixes such as `.io` and `.ai` are not treated as country hints. The original page supplies language hints even when content filters remove the HTML element.

## Empty results and errors

No valid numbers produce `phone_numbers: []`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"phone-numbers"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser runs on page HTML after [content filtering](https://docs.context.dev/scrape/content-filtering.md). [Browser actions](https://docs.context.dev/scrape/browser-actions.md) can change the page before extraction, and [browser profiles](https://docs.context.dev/scrape/browser-profiles.md) can provide an authenticated session. Cached HTML can be reused; set `maxAgeMs: 0` for fresh data. [Timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md) and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) also apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.