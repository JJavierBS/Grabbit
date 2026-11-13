# Yelp reviews

> Read public Yelp business reviews, 20 per page, newest first.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "yelp-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "yelp-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use an HTTPS Yelp business URL, `yelp.com/biz/{alias}`. [Yelp search](https://docs.context.dev/scrape/prebuilt-parsers/yelp-search.md) returns these URLs. Reviews are always sorted newest first. The optional `start` parameter is a zero-based offset; each page contains up to 20 reviews.

```json theme={null}
{
  "url": "https://www.yelp.com/biz/gary-danko-san-francisco",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "yelp-reviews"
  }
}
```

`sort_by=date_desc` is accepted; other sort orders and non-empty `q`, `rr`, `rating`, or `review_filter` parameters are rejected. Single-review links using `hrid` and tracking parameters are accepted, but those parameters are ignored: the parser returns the requested page, not one selected review.

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface YelpReviewsOutput {
  type: "yelp-reviews";
  requested: true;
  success: true;
  data: {
    business: {
      id: string;
      name: string;
      url: string;
      rating: number;
      review_count: number;
    } | null;
    pagination: {
      offset: number;
      limit: 20;
      next_offset: number | null;
    };
    reviews: YelpReview[];
  };
}
```

## Review fields

```typescript theme={null}
interface YelpReview {
  id: string;
  url: string;
  rating: number;
  text: string;
  updated_at: string | null;
  author: {
    id: string | null;
    url: string | null;
    name: string | null;
    location: string | null;
    review_count: number | null;
  };
}
```

`text` is the full review. `updated_at` is Yelp's last-modified time in ISO 8601 format, not the original publication date. Review photos and owner replies are not included.

`author.id` is the reviewer's Yelp user ID, the `userid` in their profile URL. Use it, not `name`, to identify a reviewer across businesses and pages: Yelp shows names like "Alex P.", which many reviewers share. `author.url` links to the reviewer's profile, `https://www.yelp.com/user_details?userid={id}`. Both are `null` when Yelp does not return an ID.

There is no total review count in `pagination`. A full page sets `next_offset`, but the next page may still be empty. An empty page returns `reviews: []`, `business: null`, and `next_offset: null`.

Illustrative `parsed.data` with one review:

```json theme={null}
{
  "business": {
    "id": "example-id",
    "name": "Example Coffee",
    "url": "https://www.yelp.com/biz/example-coffee-san-francisco",
    "rating": 5,
    "review_count": 1
  },
  "pagination": {
    "offset": 0,
    "limit": 20,
    "next_offset": null
  },
  "reviews": [
    {
      "id": "example-review-id",
      "url": "https://www.yelp.com/biz/example-coffee-san-francisco?hrid=example-review-id",
      "rating": 5,
      "text": "Friendly staff and good coffee.",
      "updated_at": "2026-10-01T12:00:00.000Z",
      "author": {
        "id": "example-user-id",
        "url": "https://www.yelp.com/user_details?userid=example-user-id",
        "name": "Example Reviewer",
        "location": "San Francisco, CA",
        "review_count": 3
      }
    }
  ]
}
```

## Errors and request options

Unsupported URLs, sort orders, or review filters fail with `INPUT_VALIDATION_ERROR`; an unavailable or invalid Yelp response fails with `WEBSITE_ACCESS_ERROR`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser fetches Yelp data separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.