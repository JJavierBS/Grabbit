# Instagram post

> Get an Instagram post or reel with its stats, media, and top comments.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "instagram-post"}`. Read the result in `parsed.data`, with `parsed.type: "instagram-post"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a public post or reel URL: `instagram.com/p/{shortcode}/`, `/reel/{shortcode}/`, or `/tv/{shortcode}/`. A username before the path, as in `instagram.com/natgeo/reel/{shortcode}/`, also works.

```json theme={null}
{
  "url": "https://www.instagram.com/reel/DeckcQnA23l/",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "instagram-post"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface InstagramPostOutput {
  type: "instagram-post";
  requested: true;
  success: true;
  data: InstagramPost & { comments: InstagramComment[] };
}
```

## Post fields

The [Instagram profile](https://docs.context.dev/scrape/prebuilt-parsers/instagram-profile.md) and [Instagram feed](https://docs.context.dev/scrape/prebuilt-parsers/instagram-feed.md) parsers return posts in the same shape.

```typescript theme={null}
interface InstagramPost {
  id: string;
  shortcode: string;
  url: string;
  type: "image" | "video" | "carousel" | "reel" | null;
  posted_at: string | null;
  caption: string | null;
  hashtags: string[];
  mentions: string[];
  owner: { id: string | null; username: string | null } | null;
  like_count: number | null;
  comment_count: number | null;
  view_count: number | null;
  video_duration_seconds: number | null;
  thumbnail_url: string | null;
  video_url: string | null;
  tagged_users: string[];
  collaborators: string[];
  location: { id: string; name: string | null } | null;
  is_paid_partnership: boolean | null;
  sponsors: string[];
}

interface InstagramComment {
  id: string;
  text: string | null;
  created_at: string;
  like_count: number | null;
  reply_count: number | null;
  author: {
    id: string;
    username: string;
    is_verified: boolean;
    profile_pic_url: string | null;
  };
}
```

All fields are present. Unavailable scalar values are `null`; missing lists are `[]`. IDs are strings, and dates are ISO 8601. `hashtags` and `mentions` are read from the caption, without `#` or `@`. `tagged_users`, `collaborators`, and `sponsors` are usernames. `view_count` and `video_duration_seconds` are `null` for images. Media URLs are signed Instagram CDN links that expire, so download them promptly if you need to keep them.

`comments` holds the top comments Instagram shows publicly, usually about 14; `comment_count` is the total. Replies and further comments need an Instagram login and aren't returned. `is_paid_partnership` is `null` when the post page doesn't state it; the [profile parser](https://docs.context.dev/scrape/prebuilt-parsers/instagram-profile.md) reports paid partnerships and sponsors for a profile's latest posts.

## Empty results and errors

A deleted or nonexistent post produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"instagram-post"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public Instagram data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.