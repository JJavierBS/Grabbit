# Instagram feed

> Get the top Instagram posts for a hashtag or keyword, or the recent posts at a location.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "instagram-feed"}`. Read the result in `parsed.data`, with `parsed.type: "instagram-feed"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use one of these URLs:

| URL | Posts |
| - | - |
| `instagram.com/explore/tags/{hashtag}/` | Top posts for the hashtag |
| `instagram.com/popular/{keyword}/` | Top posts for the keyword |
| `instagram.com/explore/locations/{id}/{slug}/` | Recent posts at the location; the slug is optional |

```json theme={null}
{
  "url": "https://www.instagram.com/explore/tags/running/",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "instagram-feed"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface InstagramFeedOutput {
  type: "instagram-feed";
  requested: true;
  success: true;
  data: { posts: InstagramPost[] };
}
```

## Post fields

Each post uses the [post shape](https://docs.context.dev/scrape/prebuilt-parsers/instagram-post.md#post-fields), without duplicates.

Without a login, Instagram shows hashtags as its keyword page, so hashtag and keyword URLs return the same ranked posts. Broad keywords return a couple of hundred posts; narrow ones return about 12. Keyword posts carry the `shortcode`, `url`, `owner`, `thumbnail_url`, and `view_count`, plus the `caption` and `video_url` when Instagram shows them; their other fields are `null` or `[]`. Location posts carry the full post fields, about 15 to 20 at a time. For a keyword post's full details, pass its `url` to [Instagram post](https://docs.context.dev/scrape/prebuilt-parsers/instagram-post.md).

## Empty results and errors

A hashtag or keyword Instagram has no public page for produces `NOT_FOUND`; this includes rare terms and some non-English hashtags. A location with no public posts, or an unknown location ID, produces `posts: []`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"instagram-feed"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public Instagram data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.