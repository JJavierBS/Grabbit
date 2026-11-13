# TikTok profile

> Get a TikTok profile with its follower, like, and video counts.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-profile"}`. Read the result in `parsed.data`, with `parsed.type: "tiktok-profile"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a profile URL, `tiktok.com/@{username}`. Query parameters are ignored.

```json theme={null}
{
  "url": "https://www.tiktok.com/@tiktok",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-profile"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokProfileOutput {
  type: "tiktok-profile";
  requested: true;
  success: true;
  data: TikTokProfile;
}
```

## Profile fields

```typescript theme={null}
interface TikTokProfile {
  id: string;
  username: string;
  nickname: string | null;
  biography: string | null;
  avatar_url: string | null;
  bio_link: string | null;
  sec_uid: string | null;
  created_at: string | null;
  follower_count: number | null;
  following_count: number | null;
  friend_count: number | null;
  like_count: number | null;
  video_count: number | null;
  liked_video_count: number | null;
  is_verified: boolean;
  is_private: boolean;
  is_business_account: boolean;
  is_seller: boolean;
  is_organization: boolean;
  category: string | null;
}
```

All fields are present. Unavailable scalar values are `null`. Counts are exact. `like_count` is the total likes across the profile's videos, `liked_video_count` is how many videos the profile has liked, and `friend_count` is mutual follows. `sec_uid` is TikTok's stable profile identifier, and `created_at` is ISO 8601. `category` is set for business accounts.

Private profiles return their profile fields with `is_private: true`. A profile's videos and follower lists aren't returned: use [TikTok feed](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-feed.md) and [TikTok followers](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-followers.md). For a single post, use [TikTok video](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-video.md).

## Empty results and errors

A nonexistent or removed profile produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"tiktok-profile"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.