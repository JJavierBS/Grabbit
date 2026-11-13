# Reddit search

> Read Reddit search results as posts, communities, or accounts, with up to 1,000 results per request.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "reddit-search"}`. Read the result in `parsed.data`, with `parsed.type: "reddit-search"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a Reddit search URL with a `q` query:

* `reddit.com/search?q={query}` searches all of Reddit.
* `reddit.com/r/{subreddit}/search?q={query}` searches one subreddit.

`www`, `old`, `new`, `np`, `m`, and `sh` subdomains of `reddit.com` are accepted.

The URL's query parameters choose what is returned:

| Parameter | Values |
| - | - |
| `type` | `link` or omitted for posts, `sr` for communities, `user` for accounts. `posts`, `communities`, `users`, and `people` are also accepted. |
| `sort` | Post searches only: `relevance` (default), `hot`, `top`, `new`, or `comments`. |
| `t` | Post searches only: `hour`, `day`, `week`, `month`, `year`, or `all` (default). |

The optional `parseParams.limit` caps the number of results, from 1 to 1,000, with a default of 100. Results keep the order Reddit returns them in.

```json theme={null}
{
  "url": "https://www.reddit.com/r/programming/search?q=rust&sort=top&t=month",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "reddit-search",
    "limit": 50
  }
}
```

## Output

When `parsed.success` is `true`, `parsed.data` has one of three shapes, depending on `type`:

```typescript theme={null}
type RedditSearchData =
  | {
      query: string;
      subreddit: string | null;
      sort: "relevance" | "hot" | "top" | "new" | "comments";
      time: "hour" | "day" | "week" | "month" | "year" | "all";
      posts: RedditPost[];
      has_more: boolean;
    }
  | {
      query: string;
      communities: RedditCommunity[];
      has_more: boolean;
    }
  | {
      query: string;
      users: RedditUser[];
      has_more: boolean;
    };
```

`posts` use the [Reddit post shape](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md#post-fields). `subreddit` is the subreddit searched, or `null` for a site-wide search. `has_more` is `true` when Reddit has results beyond those returned.

## Community fields

```typescript theme={null}
interface RedditCommunity {
  id: string;
  name: string;
  title: string | null;
  description: string | null;
  sidebar: string | null;
  url: string;
  subscriber_count: number | null;
  created_at: string | null;
  type: string | null;
  is_nsfw: boolean;
  is_quarantined: boolean;
  language: string | null;
  category: string | null;
  icon_url: string | null;
  banner_url: string | null;
  primary_color: string | null;
  submission_type: string | null;
  allows_images: boolean | null;
  allows_videos: boolean | null;
  allows_galleries: boolean | null;
  allows_polls: boolean | null;
}
```

`name` is the subreddit name without `r/`. `description` is the short public description, and `sidebar` is the longer sidebar text. `type` is Reddit's subreddit type, such as `public` or `restricted`. Dates are ISO 8601.

## Account fields

```typescript theme={null}
interface RedditUser {
  id: string | null;
  username: string;
  display_name: string | null;
  bio: string | null;
  url: string;
  created_at: string | null;
  total_karma: number | null;
  post_karma: number | null;
  comment_karma: number | null;
  awardee_karma: number | null;
  awarder_karma: number | null;
  is_verified: boolean | null;
  has_verified_email: boolean | null;
  is_suspended: boolean;
  is_employee: boolean;
  is_moderator: boolean | null;
  is_premium: boolean | null;
  is_nsfw: boolean;
  accepts_followers: boolean | null;
  avatar_url: string | null;
  banner_url: string | null;
}
```

The [Reddit user](https://docs.context.dev/scrape/prebuilt-parsers/reddit-user.md) parser returns the same account shape for a single profile.

## Errors and request options

URLs that aren't Reddit search URLs, or that have no `q`, fail with `INPUT_VALIDATION_ERROR`. Reddit blocks and refusals fail with `WEBSITE_ACCESS_ERROR`. If later result pages can't be read in time, the results already read are returned with `has_more: true`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser reads public Reddit data without logging in, separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.