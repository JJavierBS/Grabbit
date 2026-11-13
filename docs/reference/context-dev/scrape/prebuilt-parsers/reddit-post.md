# Reddit post

> Read a public Reddit post with its media and up to 1,000 comments as a nested tree.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "reddit-post"}`. Read the result in `parsed.data`, with `parsed.type: "reddit-post"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a Reddit post URL:

* `reddit.com/r/{subreddit}/comments/{id}`, with or without the title slug
* `reddit.com/user/{username}/comments/{id}` for a post on a profile
* `reddit.com/comments/{id}` or `redd.it/{id}`

`www`, `old`, `new`, `np`, `m`, and `sh` subdomains of `reddit.com` are accepted. Share links such as `reddit.com/r/{subreddit}/s/{code}` are not; open them first and use the post URL they redirect to.

The URL's `sort` query parameter orders the comments: `best` (default), `top`, `new`, `controversial`, `old`, or `qa`. The optional `parseParams.limit` caps the total number of comments, from 1 to 1,000, with a default of 100.

```json theme={null}
{
  "url": "https://www.reddit.com/r/programming/comments/1x97lsb/its_still_ok_to_enjoy_programming/?sort=top",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "reddit-post",
    "limit": 200
  }
}
```

Comments are filled shallowest first: every top-level comment is read before deeper replies, so a limit keeps whole conversations instead of one long branch.

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface RedditPostOutput {
  type: "reddit-post";
  requested: true;
  success: true;
  data: {
    post: RedditPost;
    comments: RedditThreadComment[];
    comment_sort: "confidence" | "top" | "new" | "controversial" | "old" | "qa";
    has_more_comments: boolean;
  };
}
```

`comment_sort` reports the order used; Reddit's API calls `best` `confidence`. `has_more_comments` is `true` when the thread has comments beyond those returned.

## Post fields

```typescript theme={null}
interface RedditPost {
  id: string;
  title: string;
  body: string | null;
  type: "text" | "link" | "image" | "gallery" | "video";
  url: string;
  link_url: string | null;
  domain: string | null;
  subreddit: string;
  author: string | null;
  author_flair: string | null;
  flair: string | null;
  posted_at: string;
  edited_at: string | null;
  score: number | null;
  upvote_ratio: number | null;
  comment_count: number | null;
  crosspost_count: number | null;
  award_count: number | null;
  is_nsfw: boolean;
  is_spoiler: boolean;
  is_locked: boolean;
  is_stickied: boolean;
  is_archived: boolean;
  is_original_content: boolean;
  distinguished: string | null;
  removed_by: string | null;
  thumbnail_url: string | null;
  images: {
    url: string;
    width: number | null;
    height: number | null;
    caption: string | null;
  }[];
  video: {
    url: string;
    hls_url: string | null;
    duration_seconds: number | null;
    width: number | null;
    height: number | null;
    has_audio: boolean;
  } | null;
  crosspost_parent_id: string | null;
}
```

* `body` is the post text as Markdown, and `null` for link and media posts.
* `url` is the post on Reddit; `link_url` is the page a link post points to, and `null` for text posts.
* `author` is `null` for deleted accounts. Dates are ISO 8601.
* `images` lists every gallery image in order, or the preview image of other posts.
* `video.url` is an MP4 without sound. Use `hls_url` for the stream with audio.
* A crosspost carries the media of the original post, whose ID is in `crosspost_parent_id`.

## Comment fields

```typescript theme={null}
interface RedditThreadComment {
  id: string;
  author: string | null;
  body: string | null;
  score: number | null;
  posted_at: string | null;
  depth: number | null;
  parent_id: string | null;
  url: string | null;
  is_submitter: boolean;
  is_deleted: boolean;
  is_collapsed: boolean;
  award_count: number;
  author_avatar_url: string | null;
  replies: RedditThreadComment[];
}
```

`comments` holds the top-level comments, each with its `replies`. `depth` starts at 0, and `parent_id` is the ID of the comment replied to, or `null` at the top level. `body` is Markdown. `is_submitter` marks comments by the post's author. Deleted comments keep their place in the tree with `is_deleted: true` and a `null` URL, so their replies stay attached.

Illustrative `parsed.data` for a link post, with `limit: 2` and one shortened reply:

```json theme={null}
{
  "post": {
    "id": "1x97lsb",
    "title": "It's still OK to enjoy programming",
    "body": null,
    "type": "link",
    "url": "https://www.reddit.com/r/programming/comments/1x97lsb/its_still_ok_to_enjoy_programming/",
    "link_url": "https://chriskiehl.com/article/it-is-still-ok-to-enjoy-programming",
    "domain": "chriskiehl.com",
    "subreddit": "programming",
    "author": "chriskiehl",
    "author_flair": null,
    "flair": null,
    "posted_at": "2026-10-18T16:33:28.000Z",
    "edited_at": null,
    "score": 683,
    "upvote_ratio": 0.87,
    "comment_count": 269,
    "crosspost_count": 0,
    "award_count": 0,
    "is_nsfw": false,
    "is_spoiler": false,
    "is_locked": false,
    "is_stickied": false,
    "is_archived": false,
    "is_original_content": false,
    "distinguished": null,
    "removed_by": null,
    "thumbnail_url": null,
    "images": [],
    "video": null,
    "crosspost_parent_id": null
  },
  "comments": [
    {
      "id": "phjrwt1",
      "author": "ficiek",
      "body": "This article manages to exist by conveniently completely missing why everyone is upset. The correct title for this article is \"It's still OK to enjoy programming AS A HOBBY\".",
      "score": 566,
      "posted_at": "2026-10-18T18:50:47.379Z",
      "depth": 0,
      "parent_id": null,
      "url": "https://www.reddit.com/r/programming/comments/1x97lsb/comment/phjrwt1/",
      "is_submitter": false,
      "is_deleted": false,
      "is_collapsed": false,
      "award_count": 0,
      "author_avatar_url": "https://www.redditstatic.com/avatars/defaults/v2/avatar_default_5.png",
      "replies": [
        {
          "id": "phkfg6w",
          "author": "DmitriRussian",
          "body": "I would say that even pre-AI programming jobs were rarely fun.",
          "score": 179,
          "posted_at": "2026-10-18T20:31:56.507Z",
          "depth": 1,
          "parent_id": "phjrwt1",
          "url": "https://www.reddit.com/r/programming/comments/1x97lsb/comment/phkfg6w/",
          "is_submitter": false,
          "is_deleted": false,
          "is_collapsed": false,
          "award_count": 0,
          "author_avatar_url": null,
          "replies": []
        }
      ]
    }
  ],
  "comment_sort": "top",
  "has_more_comments": true
}
```

## Errors and request options

URLs that aren't Reddit posts fail with `INPUT_VALIDATION_ERROR`. A post that doesn't exist, or was removed or made private, fails with `NOT_FOUND`; Reddit blocks and refusals fail with `WEBSITE_ACCESS_ERROR`. If the post loads but its comments can't be read in time, the post is still returned with `comments: []` and `has_more_comments: true`. Check `parsed.success` before reading `parsed.data`. A failed parse has `data: null` and can coexist with successful outputs. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

This parser reads public Reddit data without logging in, separately from the rendered page. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported. [Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.