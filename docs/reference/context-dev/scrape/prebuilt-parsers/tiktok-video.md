# TikTok video

> Get a TikTok video or photo post with its stats, music, paid partnership, and a downloadable video URL.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-video"}`. Read the result in `parsed.data`, with `parsed.type: "tiktok-video"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a public video or photo post URL: `tiktok.com/@{username}/video/{id}` or `/@{username}/photo/{id}`. Short links such as `vm.tiktok.com/...` aren't accepted; open them to get the full URL.

```json theme={null}
{
  "url": "https://www.tiktok.com/@scout2015/video/6718335390845095173",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-video"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokVideoOutput {
  type: "tiktok-video";
  requested: true;
  success: true;
  data: TikTokVideo;
}
```

## Video fields

```typescript theme={null}
interface TikTokVideo {
  id: string;
  url: string;
  type: "video" | "photo";
  posted_at: string | null;
  caption: string | null;
  hashtags: string[];
  mentions: string[];
  author: {
    id: string;
    username: string;
    nickname: string | null;
    is_verified: boolean;
    avatar_url: string | null;
  };
  view_count: number | null;
  like_count: number | null;
  comment_count: number | null;
  share_count: number | null;
  save_count: number | null;
  repost_count: number | null;
  video_duration_seconds: number | null;
  thumbnail_url: string | null;
  video_url: string | null;
  image_urls: string[];
  music: {
    id: string;
    title: string | null;
    author: string | null;
    is_original: boolean;
    url: string | null;
  } | null;
  location: {
    id: string;
    name: string | null;
    address: string | null;
    city: string | null;
    category: string | null;
  } | null;
  region: string | null;
  is_ad: boolean;
  is_paid_partnership: boolean;
  sponsors: string[];
  is_promotional_content: boolean;
  is_ai_generated: boolean;
}
```

All fields are present. Unavailable scalar values are `null`; missing lists are `[]`. IDs are strings, and `posted_at` is ISO 8601. `hashtags` and `mentions` are without `#` or `@`. Photo posts have `type: "photo"`, their images in `image_urls`, and `null` for `video_url` and `video_duration_seconds`. `region` is the two-letter country the post was created in.

`video_url` downloads the video file without cookies. It and the other media URLs are TikTok links that can expire, so download them promptly if you need to keep them.

`is_paid_partnership` is `true` when the post carries TikTok's "Paid partnership" label, and `sponsors` holds the partner brand's username. `is_promotional_content` is `true` when the creator marked the post as promoting a brand, product, or service. `is_ad` marks TikTok ads.

For the comments themselves, use [TikTok comments](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-comments.md).

## Empty results and errors

A deleted or nonexistent post produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"tiktok-video"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.