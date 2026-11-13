# TikTok feed

> List the videos of a TikTok profile, hashtag, or search.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-feed"}`. Read the result in `parsed.data`, with `parsed.type: "tiktok-feed"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

The URL selects the feed:

| URL | Videos |
| - | - |
| Profile, `tiktok.com/@{username}` | The latest 15 |
| Hashtag, `tiktok.com/tag/{name}` | The top 30 |
| Search, `tiktok.com/search?q={query}` or `tiktok.com/search/video?q={query}` | The top 12 |

```json theme={null}
{
  "url": "https://www.tiktok.com/tag/food",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-feed"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokFeedOutput {
  type: "tiktok-feed";
  requested: true;
  success: true;
  data: {
    videos: TikTokVideo[];
  };
}
```

Each video has the same fields as the [TikTok video](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-video.md#video-fields) parser, including counts, paid-partnership flags, and `video_url`. Only the first page is returned.

## Empty results and errors

A profile, hashtag, or search with no videos returns `videos: []`. A nonexistent profile or hashtag produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"tiktok-feed"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.