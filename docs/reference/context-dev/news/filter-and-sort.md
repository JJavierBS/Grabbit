# Filter and sort

> Select news by one source category, date window, and ordering.

`filterBy` accepts one category filter at a time, plus an optional date range. Combining categories returns a validation error.

## Find press releases

Send this body to `POST /news/search`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "searchBy": {
    "type": "entity",
    "entity": {
      "type": "domain",
      "domain": "stripe.com"
    }
  },
  "filterBy": {
    "articleType": [
      "press_release"
    ],
    "date": {
      "from": 1785542400000,
      "to": 1788220799999
    }
  },
  "sortBy": {
    "type": "newest"
  }
}
```

## Filter categories

| Field | Values | Max items |
| - | - | - |
| `sourceDomain` | Publisher domains, each 1–253 characters. | 3 |
| `sourceCountry` | Lowercase ISO 3166-1 alpha-2 country codes. | 3 |
| `articleLanguage` | Supported language codes, such as `["en", "de"]`. | 3 |
| `articleType` | `editorial`, `press_release`, `regulatory_filing`, `advisory`. | 3 |

Language filters keep articles whose language cannot be detected.

`date.from` and `date.to` are inclusive epoch milliseconds; `from` must be at most `to`. Either bound can be omitted. The example window covers August 2026 in UTC; calculate new bounds for a rolling window.

Filters work the same for natural-language and company searches. For company searches, `sortBy.type` is `newest` (default) or `relevance`. Natural-language searches are always ranked by relevance, with a boost for recent articles, and `newest` returns a validation error. Use the same filters and sort for every [pagination request](https://docs.context.dev/news/paginate.md).


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.