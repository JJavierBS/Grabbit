# App Store reviews

> Get up to 500 recent App Store reviews for an app and storefront.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "app-store-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "app-store-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use the same app URL as the [App Store parser](https://docs.context.dev/scrape/prebuilt-parsers/app-store.md), including its numeric `id`. The two-letter country in the path selects the review storefront and defaults to `us` when omitted. The parser reads up to ten pages of 50 reviews each, requested newest first. There are no request parameters for pagination, review count, or sorting.

```json theme={null}
{
  "url": "https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "app-store-reviews"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface AppStoreReviewsOutput {
  type: "app-store-reviews";
  requested: true;
  success: true;
  data: {
    app_id: string;
    reviews: AppStoreReview[];
  };
}
```

## Review fields

```typescript theme={null}
interface AppStoreReview {
  id: string;
  author: string;
  rating: number;
  title: string | null;
  text: string | null;
  created_at: string;
  app_version: string | null;
  helpful_votes: number | null;
  total_votes: number | null;
}
```

All review fields are present. Optional source values are `null` when unavailable. `created_at` is an ISO 8601 timestamp derived from the feed entry’s update time. Reviews are specific to the selected storefront; this is not a complete worldwide review history.

## Empty results and errors

No reviews produce `reviews: []`. An unknown app can also return an empty feed, so an empty list does not establish that the app exists. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"app-store-reviews"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page, using a US exit. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.