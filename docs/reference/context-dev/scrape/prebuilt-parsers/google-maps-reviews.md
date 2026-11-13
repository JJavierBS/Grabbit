# Google Maps reviews

> Get up to 1,000 Google Maps reviews for a place, newest, oldest, most relevant, or by rating.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "google-maps-reviews"}`. Read the result in `parsed.data`, with `parsed.type: "google-maps-reviews"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

The URL identifies the place. These forms are accepted:

* A Maps place URL, such as `https://www.google.com/maps/place/...`. When the URL carries a feature ID (`!1s0x…:0x…`), that exact place is used.
* A CID URL, such as `https://maps.google.com/?cid=16537904221077587530`. Signed CIDs, as returned by the [Google Maps parser](https://docs.context.dev/scrape/prebuilt-parsers/google-maps.md), work too.
* A reviews URL, such as `https://search.google.com/local/reviews?placeid=ChIJ…`.
* A Maps search URL. The first result is used.

The `google_maps_url` and `google_reviews_url` fields of [Google Maps parser](https://docs.context.dev/scrape/prebuilt-parsers/google-maps.md) results both work as input.

Two optional fields on `parseParams` control the result:

| Field | Values | Default |
| - | - | - |
| `sort` | `newest`, `oldest`, `relevant`, `highest`, `lowest` | `newest` |
| `limit` | 1 to 1,000 | 100 |

`newest`, `relevant`, `highest`, and `lowest` follow Google's own orders. `oldest` returns the earliest reviews first, ordered by exact posting time, which Google itself does not offer. Other parsers reject `sort`; `limit` is also accepted by the Reddit parsers, [post](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md), [search](https://docs.context.dev/scrape/prebuilt-parsers/reddit-search.md), [subreddit](https://docs.context.dev/scrape/prebuilt-parsers/reddit-subreddit.md), and [user](https://docs.context.dev/scrape/prebuilt-parsers/reddit-user.md), and rejected by the rest.

```json theme={null}
{
  "url": "https://maps.google.com/?cid=16537904221077587530",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "google-maps-reviews",
    "sort": "oldest",
    "limit": 50
  }
}
```

Larger limits take longer: about 20 seconds for the oldest 1,000 reviews of a large place, and about 45 seconds for 1,000 in Google's orders. Raise [`timeoutOpts.milliseconds`](https://docs.context.dev/scrape/timeouts-and-errors) when you need headroom beyond the 90-second default.

## Output

Field names and shapes match Serper's Google reviews response, so existing Serper integrations work unchanged. `featureId`, `cid`, and `sort` at the top level, and `user.isLocalGuide`, `language`, and `details` on each review, are additions.

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface GoogleMapsReviewsOutput {
  type: "google-maps-reviews";
  requested: true;
  success: true;
  data: {
    reviews: GoogleMapsReview[];
    featureId: string;
    cid: string | null;
    sort: "newest" | "oldest" | "relevant" | "highest" | "lowest";
  };
}
```

`featureId` is the place's Maps feature ID. `cid` is the same signed CID the Google Maps parser returns, so you can join the two outputs. `sort` is the order used.

## Review fields

```typescript theme={null}
interface GoogleMapsReview {
  rating: number | null;
  date: string | null;
  isoDate: string | null;
  snippet?: string;
  translatedSnippet?: string;
  likes: number;
  user: {
    name: string | null;
    thumbnail: string | null;
    link: string | null;
    reviews: number | null;
    photos: number | null;
    isLocalGuide: boolean;
  };
  media?: {
    type: "image";
    imageUrl: string;
    caption?: string;
  }[];
  response?: {
    date: string | null;
    snippet: string;
  };
  link: string | null;
  id: string;
  language: string | null;
  details: Record<string, string | number>;
}
```

Optional keys are omitted, not `null`, when empty, matching Serper. Other unavailable values are `null`.

* `date` is Google's relative label, such as `"3 months ago"`, and `isoDate` is the exact posting time as an ISO 8601 timestamp.
* `snippet` is the review in its original language, and `language` is that language's code. `translatedSnippet` is Google's English translation, omitted when there is none, such as for English reviews. Line breaks are `\n`, and rating-only reviews have no `snippet`.
* `likes` counts every reaction on the review.
* `user` is the reviewer: `thumbnail` is the avatar URL, `link` the contributor profile, and `reviews` and `photos` the contributor's review and photo counts.
* `media` lists the review's photos and is omitted when there are none. `caption` is omitted when empty.
* `response` is the owner's reply, omitted when the owner hasn't replied. Google only gives a relative `date` for replies.
* `link` is the review's permalink.
* `details` holds the guided answers, such as `{"Meal type": "Breakfast", "Food": 5}` for restaurants or `{"Rooms": 4, "Location": 5}` for hotels, and is `{}` when there are none.

## Empty results and errors

A place without reviews returns `reviews: []`. Google answers an unknown CID the same way, so an empty list does not establish that the place exists. A search or place URL that matches no place fails with `NOT_FOUND`.

Reviews posted in the last few hours can take a while to appear in every Google region, so a very fresh review may be missing from one request and present in the next.

Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"google-maps-reviews"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser fetches source data separately from the rendered page, using a US exit and English labels. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.