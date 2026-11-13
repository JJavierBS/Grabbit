# Reddit subreddit

> Read a subreddit's details, rules, and up to 1,000 posts from any of its tabs.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "reddit-subreddit"}`. Read the result in `parsed.data`, with `parsed.type: "reddit-subreddit"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a subreddit URL, `reddit.com/r/{subreddit}`, optionally followed by a tab: `/hot` (default), `/new`, `/top`, `/rising`, or `/controversial`. `www`, `old`, `new`, `np`, `m`, and `sh` subdomains of `reddit.com` are accepted.

For `/top` and `/controversial`, the URL's `t` query parameter sets the time range: `hour`, `day` (default), `week`, `month`, `year`, or `all`. Other tabs ignore it.

The optional `parseParams.limit` caps the number of posts, from 1 to 1,000, with a default of 100.

```json theme={null}
{
  "url": "https://www.reddit.com/r/programming/top/?t=week",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "reddit-subreddit",
    "limit": 25
  }
}
```

## Output

When `parsed.success` is `true`, `parsed.data` has this shape:

```typescript theme={null}
interface RedditSubredditData {
  subreddit: RedditCommunity | null;
  rules: RedditRule[] | null;
  sort: "hot" | "new" | "top" | "rising" | "controversial";
  time: "hour" | "day" | "week" | "month" | "year" | "all" | null;
  posts: RedditPost[];
  has_more: boolean;
}

interface RedditRule {
  name: string;
  description: string | null;
  applies_to: "posts" | "comments" | "all" | null;
  violation_reason: string | null;
  created_at: string | null;
}
```

* `subreddit` uses the [community shape](https://docs.context.dev/scrape/prebuilt-parsers/reddit-search.md#community-fields) of the Reddit search parser.
* `posts` use the [Reddit post shape](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md#post-fields) and follow the tab's order. Stickied posts have `is_stickied: true`.
* `time` is `null` unless the tab is `top` or `controversial`.
* `r/all` and `r/popular` are site-wide feeds, so they return posts with `subreddit` and `rules` set to `null`.
* `has_more` is `true` when the tab has posts beyond those returned.

## Errors and request options

URLs that aren't subreddit URLs fail with `INPUT_VALIDATION_ERROR`. A subreddit that doesn't exist fails with `NOT_FOUND`. Private and quarantined subreddits, Reddit blocks, and refusals fail with `WEBSITE_ACCESS_ERROR`. If later post pages can't be read in time, the posts already read are returned with `has_more: true`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser reads public Reddit data without logging in, separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.