# JSON

> Extract page facts into an object that follows your JSON Schema.

Enable `formats.json` and provide `jsonParams.schema`. An AI model reads the page’s Markdown, JSON-LD, and meta tags and returns an object in `json.data`.

## Define the object

Send this body to `POST /web/scrape`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "json": true
  },
  "jsonParams": {
    "schema": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "contact_email": {
          "type": [
            "string",
            "null"
          ]
        }
      },
      "required": [
        "title",
        "contact_email"
      ]
    },
    "instructions": "Use only facts stated on the page."
  }
}
```

Abridged response:

```json theme={null}
{"json":{"requested":true,"success":true,"data":{"title":"Example Domain","contact_email":null}}}
```

## Design for missing facts

Use optional or nullable fields for facts a page might omit. Required, non-nullable fields receive a best-effort value and can introduce guesses. In optional or nullable fields, numbers that do not appear on the page and punctuation-only strings are dropped: nullable fields return `null` and optional fields are omitted. Enum values, whole numbers up to 12, and fields named for a computed value (such as `total`, `count`, or `average`) are kept. Review extracted values before using them for consequential decisions.

The schema must describe a top-level object. Wrap a list in an object property:

```json theme={null}
{"type":"object","properties":{"products":{"type":"array","items":{"type":"object","properties":{"name":{"type":"string"}}}}}}
```

Open objects, such as a free-form map declared with `additionalProperties`, are accepted. Zod users can pass `z.toJSONSchema()` output. `jsonParams.instructions` can specify which facts to prioritize or how to interpret fields.

## Choose an extraction method

| Need | Use |
| - | - |
| Known CSS selectors and exact page values | [Custom parser](https://docs.context.dev/scrape/parse-fields.md) |
| Interpret one page into a custom schema | JSON |
| Standard product details | [Product](https://docs.context.dev/scrape/product.md) |
| Research across the web | [Answers](https://docs.context.dev/answers/overview) |

## Limits

Extraction from page text adds a [Scrape modifier](https://docs.context.dev/account/credits.md#scrape-modifiers) charge; a failed extraction or a page with no text adds nothing.

Schemas are limited to 50 KB when serialized; instructions to 2,000 characters. Extraction reads up to 100,000 characters of Markdown after [content filtering](https://docs.context.dev/scrape/content-filtering.md), plus up to 20,000 characters of JSON-LD and meta tags. On a longer page it keeps the sections that best match your schema, instructions, and URL fragment, and a successful output includes `isTruncated: true`; values found only in omitted sections can be missing. A page with no text returns `{}`. A failed or timed-out extraction has `success: false`, `data: null`, and an `error_code` and `message`.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.