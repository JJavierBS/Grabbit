# TikTok user search

> Find TikTok accounts that match a search query.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-user-search"}`. Read the result in `parsed.data`, with `parsed.type` set to `"tiktok-user-search"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a user search URL, `tiktok.com/search/user?q={query}`, with a non-empty `q`. For videos that match a query, use [TikTok feed](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-feed.md) with a `tiktok.com/search?q={query}` URL.

```json theme={null}
{
  "url": "https://www.tiktok.com/search/user?q=snackpass",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-user-search"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokUserSearchOutput {
  type: "tiktok-user-search";
  requested: true;
  success: true;
  data: {
    users: TikTokSearchUser[];
  };
}
```

## User fields

```typescript theme={null}
interface TikTokSearchUser {
  id: string;
  username: string;
  nickname: string | null;
  biography: string | null;
  avatar_url: string | null;
  sec_uid: string | null;
  follower_count: number | null;
  like_count: number | null;
  is_verified: boolean;
}
```

Up to 10 accounts are returned, in TikTok's ranking. `like_count` is the total likes across the account's videos, and `sec_uid` is TikTok's stable profile identifier. For full profile fields, pass `tiktok.com/@{username}` to [TikTok profile](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-profile.md).

## Empty results and errors

A query with no matching accounts returns `users: []`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"tiktok-user-search"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.