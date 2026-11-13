# TikTok followers and following

> List the accounts that follow a TikTok profile, or that it follows.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-followers"}` for a profile's followers, or `"parser": "tiktok-following"` for the accounts it follows. Read the result in `parsed.data`, with `parsed.type` set to the parser name. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with these parsers. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a profile URL, `tiktok.com/@{username}`. Query parameters are ignored.

```json theme={null}
{
  "url": "https://www.tiktok.com/@nasa",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-followers"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokFollowersOutput {
  type: "tiktok-followers" | "tiktok-following";
  requested: true;
  success: true;
  data: {
    users: TikTokProfile[];
  };
}
```

Each account has the same fields as the [TikTok profile](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-profile.md#profile-fields) parser. Up to 30 accounts are returned, from the first page of the list.

## Empty results and errors

A profile with no followers or followed accounts returns `users: []`, and so does a profile that hides the list. A nonexistent profile produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains the requested parser name even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

These parsers read public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change their results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with these parsers. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.