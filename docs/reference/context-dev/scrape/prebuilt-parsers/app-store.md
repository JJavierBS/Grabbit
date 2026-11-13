# App Store

> Get app details, ratings, pricing, and screenshots from the App Store.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "app-store"}`. Read the result in `parsed.data`, with `parsed.type: "app-store"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use an `apps.apple.com` app URL with a numeric `id` in the path. The app name is optional, so `https://apps.apple.com/us/app/id324684580` also works. The two-letter country in the path selects the storefront, including prices and currency, and defaults to `us` when omitted.

```json theme={null}
{
  "url": "https://apps.apple.com/us/app/spotify-music-and-podcasts/id324684580",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "app-store"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface AppStoreOutput {
  type: "app-store";
  requested: true;
  success: true;
  data: AppStoreApp;
}
```

## App fields

```typescript theme={null}
interface AppStoreApp {
  app_id: string;
  bundle_id: string | null;
  url: string | null;
  name: string | null;
  description: string | null;
  whats_new: string | null;
  developer: {
    name: string | null;
    id: string | null;
    url: string | null;
    website: string | null;
  };
  seller: string | null;
  category: { name: string | null; id: string | null };
  genres: string[];
  rating: number | null;
  rating_count: number | null;
  current_version_rating: number | null;
  current_version_rating_count: number | null;
  price: {
    amount: number | null;
    currency: string | null;
    formatted: string | null;
    is_free: boolean;
  };
  content_rating: string | null;
  advisories: string[];
  version: string | null;
  min_ios_version: string | null;
  file_size_bytes: number | null;
  languages: string[];
  released_at: string | null;
  updated_at: string | null;
  icon_url: string | null;
  screenshot_urls: string[];
  ipad_screenshot_urls: string[];
  apple_tv_screenshot_urls: string[];
  has_game_center: boolean | null;
}
```

All fields are present. Unavailable scalar values are `null`; missing lists are `[]`. `app_id`, developer IDs, and category IDs are strings. `file_size_bytes` is a number when available. `price.amount` is in currency units. `released_at` and `updated_at` contain the source date strings. For reviews, use [App Store reviews](https://docs.context.dev/scrape/prebuilt-parsers/app-store-reviews.md).

## Empty results and errors

An app missing from the selected storefront produces `NOT_FOUND`. Try the correct country in the URL if the app is available in another storefront. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"app-store"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page, using a US exit. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.