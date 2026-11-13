# Google Play reviews

> Get up to 200 recent Google Play reviews for an app.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "google-play-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "google-play-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use the same Google Play app details URL as the [Google Play parser](https://docs.context.dev/scrape/prebuilt-parsers/google-play.md), with a package name in `id`. Optional `hl` and `gl` parameters control the locale and default to `en` and `us`. The parser requests up to 200 reviews, newest first. There are no request parameters for pagination, review count, or sorting.

```json theme={null}
{
  "url": "https://play.google.com/store/apps/details?id=com.spotify.music&hl=en&gl=us",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "google-play-reviews"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface GooglePlayReviewsOutput {
  type: "google-play-reviews";
  requested: true;
  success: true;
  data: {
    app_id: string;
    reviews: GooglePlayReview[];
  };
}
```

## Review fields

```typescript theme={null}
interface GooglePlayReview {
  id: string | null;
  author: string | null;
  author_avatar_url: string | null;
  rating: number | null;
  text: string | null;
  created_at: string | null;
  thumbs_up: number | null;
  app_version: string | null;
  developer_reply: {
    text: string;
    replied_at: string | null;
  } | null;
}
```

All review fields are present. Unavailable values are `null`. `created_at` and `developer_reply.replied_at` are ISO 8601 timestamps. `developer_reply` is `null` when no reply text is available.

## Empty results and errors

No reviews produce `reviews: []`. Google Play also returns an empty review list for an unknown app ID, so an empty list does not establish that the app exists. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"google-play-reviews"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page, using a US exit. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.