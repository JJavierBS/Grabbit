# Yelp search

> Find Yelp businesses in organic search order, with pagination.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "yelp-search"}`. Read the result in `parsed.data`, with `parsed.type: "yelp-search"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use an HTTPS Yelp search URL with non-empty `find_desc` and `find_loc` parameters. The optional `start` parameter is a zero-based result offset; each page contains up to 20 businesses.

```json theme={null}
{
  "url": "https://www.yelp.com/search?find_desc=coffee&find_loc=San+Francisco%2C+CA",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "yelp-search"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface YelpSearchOutput {
  type: "yelp-search";
  requested: true;
  success: true;
  data: {
    query: string;
    location: string;
    total: number;
    pagination: {
      offset: number;
      limit: 20;
      has_more: boolean;
      next_offset: number | null;
    };
    businesses: YelpBusiness[];
  };
}
```

## Business fields

```typescript theme={null}
interface YelpBusiness {
  id: string;
  name: string;
  url: string;
  rating: number | null;
  review_count: number | null;
  price: number | null;
  categories: string[] | null;
  address: string | null;
  coordinates: { latitude: number; longitude: number } | null;
  phone: string | null;
  photo_url: string | null;
  is_closed: boolean | null;
}
```

Businesses follow Yelp's organic search ranking; ads are excluded. `total` is Yelp's reported result count. When `pagination.next_offset` is not `null`, pass it as `start` in the next search URL.

Illustrative `parsed.data` with one business:

```json theme={null}
{
  "query": "coffee",
  "location": "San Francisco, CA",
  "total": 1,
  "pagination": {
    "offset": 0,
    "limit": 20,
    "has_more": false,
    "next_offset": null
  },
  "businesses": [
    {
      "id": "example-id",
      "name": "Example Coffee",
      "url": "https://www.yelp.com/biz/example-coffee-san-francisco",
      "rating": 4.5,
      "review_count": 12,
      "price": 2,
      "categories": ["Coffee & Tea"],
      "address": "1 Main St, San Francisco, CA 94118, US",
      "coordinates": { "latitude": 37.7, "longitude": -122.4 },
      "phone": "(415) 555-0100",
      "photo_url": null,
      "is_closed": false
    }
  ]
}
```

## Empty results and errors

A search with no matches returns `businesses: []`. Unsupported URLs or missing search parameters fail with `INPUT_VALIDATION_ERROR`; an unavailable or invalid Yelp response fails with `WEBSITE_ACCESS_ERROR`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

## Request options

This parser fetches Yelp data separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.