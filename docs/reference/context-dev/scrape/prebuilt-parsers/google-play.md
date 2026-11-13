# Google Play

> Get app details, ratings, downloads, and data safety from Google Play.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "google-play"}`. Read the result in `parsed.data`, with `parsed.type: "google-play"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a Google Play app details URL with the package name in the `id` query parameter. The optional `hl` language and `gl` country parameters control localized text, prices, and currency; they default to `en` and `us`.

```json theme={null}
{
  "url": "https://play.google.com/store/apps/details?id=com.spotify.music&hl=en&gl=us",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "google-play"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface GooglePlayOutput {
  type: "google-play";
  requested: true;
  success: true;
  data: GooglePlayApp;
}
```

## App fields

```typescript theme={null}
interface GooglePlayApp {
  app_id: string;
  url: string;
  name: string | null;
  summary: string | null;
  description: string | null;
  whats_new: string | null;
  developer: {
    name: string | null;
    id: string | null;
    url: string | null;
    website: string | null;
    email: string | null;
    phone: string | null;
    address: string | null;
  };
  offered_by: string | null;
  category: { name: string | null; id: string | null };
  tags: string[];
  rating: number | null;
  rating_count: number | null;
  rating_histogram: {
    "1": number | null;
    "2": number | null;
    "3": number | null;
    "4": number | null;
    "5": number | null;
  };
  downloads: string | null;
  downloads_min: number | null;
  downloads_exact: number | null;
  price: {
    amount: number;
    currency: string | null;
    formatted: string | null;
    is_free: boolean;
  } | null;
  in_app_purchases: string | null;
  contains_ads: boolean;
  content_rating: {
    label: string;
    descriptors: string | null;
    interactive_elements: string | null;
  } | null;
  top_chart: { label: string; rank: number | null } | null;
  version: string | null;
  min_android: { version: string; api_level: number | null } | null;
  released_at: string | null;
  updated_at: string | null;
  icon_url: string | null;
  cover_image_url: string | null;
  screenshot_urls: string[];
  trailer_url: string | null;
  privacy_policy_url: string | null;
  permissions: { group: string | null; permissions: string[] }[];
  data_safety: {
    shared: GooglePlayDataDeclaration[];
    collected: GooglePlayDataDeclaration[];
    security_practices: {
      heading: string | null;
      description: string | null;
    }[];
  } | null;
}

interface GooglePlayDataDeclaration {
  category: string | null;
  type: string | null;
  is_optional: boolean;
  purposes: string | null;
}
```

All fields are present. Nullable fields are `null` when unavailable; missing lists are `[]`. `description` and `whats_new` contain plain text. `released_at` and `updated_at` are ISO 8601 timestamps. `price.amount` is in currency units. For individual reviews, use [Google Play reviews](https://docs.context.dev/scrape/prebuilt-parsers/google-play-reviews.md).

## Empty results and errors

An app that is not on Google Play produces `NOT_FOUND`. A response without usable app data produces `WEBSITE_ACCESS_ERROR`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"google-play"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page, using a US exit. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.