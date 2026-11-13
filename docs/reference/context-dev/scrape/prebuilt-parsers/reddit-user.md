# Reddit user

> Read a public Reddit profile with karma, trophies, moderated communities, and up to 1,000 posts and comments.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "reddit-user"}`. Read the result in `parsed.data`, with `parsed.type: "reddit-user"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a profile URL, `reddit.com/user/{username}` or `reddit.com/u/{username}`, optionally followed by a tab:

* `/overview` (default) returns posts and comments.
* `/submitted` returns posts only.
* `/comments` returns comments only.

`www`, `old`, `new`, `np`, `m`, and `sh` subdomains of `reddit.com` are accepted.

The URL's `sort` query parameter orders the activity: `new` (default), `hot`, `top`, or `controversial`. For `top` and `controversial`, `t` sets the time range: `hour`, `day`, `week`, `month`, `year`, or `all` (default).

The optional `parseParams.limit` caps the posts and comments together, from 1 to 1,000, with a default of 100.

```json theme={null}
{
  "url": "https://www.reddit.com/user/spez/submitted/?sort=top&t=year",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "reddit-user",
    "limit": 50
  }
}
```

## Output

When `parsed.success` is `true`, `parsed.data` has this shape:

```typescript theme={null}
interface RedditUserData {
  user: RedditUser;
  trophies: {
    name: string;
    description: string | null;
    icon_url: string | null;
    granted_at: string | null;
    url: string | null;
  }[] | null;
  moderated_communities: {
    name: string;
    title: string | null;
    url: string;
    subscriber_count: number | null;
    icon_url: string | null;
    is_nsfw: boolean;
  }[] | null;
  tab: "overview" | "submitted" | "comments";
  sort: "new" | "hot" | "top" | "controversial";
  time: "hour" | "day" | "week" | "month" | "year" | "all" | null;
  posts: RedditPost[] | null;
  comments: RedditUserComment[] | null;
  has_more: boolean;
}
```

* `user` uses the [account shape](https://docs.context.dev/scrape/prebuilt-parsers/reddit-search.md#account-fields) of the Reddit search parser.
* `trophies` and `moderated_communities` are `null` when Reddit doesn't return them.
* `posts` use the [Reddit post shape](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md#post-fields). They are `null` on the `comments` tab, and `comments` is `null` on the `submitted` tab.
* `time` is `null` unless `sort` is `top` or `controversial`.
* `has_more` is `true` when the profile has activity beyond what was returned.

## Comment fields

```typescript theme={null}
interface RedditUserComment {
  id: string;
  author: string | null;
  body: string | null;
  score: number | null;
  posted_at: string;
  edited_at: string | null;
  url: string;
  subreddit: string;
  parent_id: string | null;
  is_submitter: boolean;
  is_stickied: boolean;
  distinguished: string | null;
  award_count: number | null;
  post: {
    id: string;
    title: string | null;
    url: string | null;
    author: string | null;
    is_nsfw: boolean;
  };
}
```

`body` is Markdown. `parent_id` is the ID of the comment replied to, or `null` for a top-level comment. `post` identifies the post the comment was left on. Dates are ISO 8601.

## Errors and request options

URLs that aren't Reddit profile URLs fail with `INPUT_VALIDATION_ERROR`. An account that doesn't exist fails with `NOT_FOUND`; Reddit blocks and refusals fail with `WEBSITE_ACCESS_ERROR`. Users who hide their activity return empty lists. Suspended accounts return their profile with `posts` and `comments` set to `null`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser reads public Reddit data without logging in, separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.