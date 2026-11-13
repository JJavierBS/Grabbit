# TikTok comments

> Get the first comments on a public TikTok video or photo post.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "tiktok-comments"}`. Read the result in `parsed.data`, with `parsed.type` set to `"tiktok-comments"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a public video or photo post URL: `tiktok.com/@{username}/video/{id}` or `/@{username}/photo/{id}`. Short links such as `vm.tiktok.com/...` aren't accepted; open them to get the full URL.

```json theme={null}
{
  "url": "https://www.tiktok.com/@nasa/video/7697300954667994381",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "tiktok-comments"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface TikTokCommentsOutput {
  type: "tiktok-comments";
  requested: true;
  success: true;
  data: {
    comments: TikTokComment[];
  };
}
```

## Comment fields

```typescript theme={null}
interface TikTokComment {
  id: string;
  text: string | null;
  posted_at: string | null;
  like_count: number | null;
  reply_count: number | null;
  is_liked_by_author: boolean;
  author: {
    id: string;
    username: string;
    nickname: string | null;
    avatar_url: string | null;
  };
}
```

Up to 20 top-level comments are returned, from the first page in TikTok's order. Replies aren't included; `reply_count` is how many each comment has. `posted_at` is ISO 8601, and `is_liked_by_author` is `true` when the post's creator liked the comment.

## Empty results and errors

A post with no visible comments returns `comments: []`, and so does a deleted or nonexistent post. Use [TikTok video](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-video.md) to check that a post exists. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"tiktok-comments"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public TikTok data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.