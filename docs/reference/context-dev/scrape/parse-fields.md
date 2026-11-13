# Custom parser

> Extract named fields and lists from a page with custom CSS rules.

Enable `formats.parse` and provide `parseParams.rules` to extract named fields using CSS selectors. `parseParams.type` defaults to `"custom"` and can also be set explicitly. Results arrive in `parsed.data` with `parsed.type: "custom"`.

Use [pre-built parsers](https://docs.context.dev/scrape/prebuilt-parsers) for supported sources without writing rules, or [JSON extraction](https://docs.context.dev/scrape/json.md) when you need to interpret page text.

## Extract custom fields

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "rules": {
      "title": "title",
      "links": {
        "selector": "a",
        "type": "list",
        "output": "@href"
      }
    }
  }
}
```

Abridged response:

```json theme={null}
{"parsed":{"type":"custom","requested":true,"success":true,"data":{"title":"Example Domain","links":["https://iana.org/help/example-domains"]}}}
```

## Rule grammar

| Rule | Result |
| - | - |
| `"h1"` | First match’s normalized text. |
| `"a@href"` | First match’s `href` attribute. |
| `{"selector":"p","output":"html"}` | First matched element’s outer HTML. |
| `{"selector":"p","type":"item"}` | First match’s text. `item` is the default `type`. |
| `{"selector":"a","type":"list","output":"text"}` | A list of text values. |
| A nested object in `output` | Fields evaluated inside each matched element. |

`type` is `item` to return the first match or `list` to return all matches. `output` is `text` (the default), `html`, an attribute such as `@href`, or nested field rules.

## Extract a list of cards

```json theme={null}
{
  "url": "https://example.com/products",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "rules": {
      "products": {
        "selector": ".product",
        "type": "list",
        "output": {
          "name": "h2",
          "url": "a@href"
        }
      }
    }
  }
}
```

Missing items are `null`; unmatched lists are `[]`. Attribute values are returned as written, so resolve relative links against the response `url`.

## Custom rule limits and page state

Provide at least one rule. Rules allow up to 100 fields, five nesting levels, and selectors up to 2,048 characters. XPath is unsupported; invalid selectors return 400.

Rules run on HTML after [content filtering](https://docs.context.dev/scrape/content-filtering.md). Cached HTML can be reused; set `maxAgeMs: 0` for fresh values. [Browser actions](https://docs.context.dev/scrape/browser-actions.md) can change the page before extraction.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.