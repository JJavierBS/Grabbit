# Instagram profile

> Get an Instagram profile with its stats, similar accounts, and latest posts.

Use `POST /web/scrape` with `formats.parse: true` and `parseParams: {"type": "prebuilt", "parser": "instagram-profile"}`. Read the result in `parsed.data`, with `parsed.type: "instagram-profile"`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

Don't send custom `rules` with this parser. For CSS selectors and rules, use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md).

## Request

Use a profile URL, `instagram.com/{username}/`. Query parameters are ignored.

```json theme={null}
{
  "url": "https://www.instagram.com/natgeo/",
  "formats": {
    "parse": true
  },
  "parseParams": {
    "type": "prebuilt",
    "parser": "instagram-profile"
  }
}
```

## Output

When `parsed.success` is `true`, the `parsed` output has this shape:

```typescript theme={null}
interface InstagramProfileOutput {
  type: "instagram-profile";
  requested: true;
  success: true;
  data: InstagramProfile;
}
```

## Profile fields

```typescript theme={null}
interface InstagramProfile {
  id: string;
  username: string;
  full_name: string | null;
  biography: string | null;
  profile_pic_url: string | null;
  external_url: string | null;
  bio_links: { url: string; title: string | null }[];
  follower_count: number | null;
  following_count: number | null;
  post_count: number | null;
  is_verified: boolean;
  is_private: boolean;
  is_business_account: boolean;
  is_professional_account: boolean;
  category: string | null;
  business_address: {
    street: string | null;
    city: string | null;
    zip_code: string | null;
    latitude: number | null;
    longitude: number | null;
  } | null;
  similar_accounts: {
    id: string;
    username: string;
    full_name: string | null;
    is_verified: boolean;
    profile_pic_url: string | null;
  }[];
  latest_posts: InstagramPost[];
}
```

All fields are present. Unavailable scalar values are `null`; missing lists are `[]`. `latest_posts` holds the 12 newest posts in the [post shape](https://docs.context.dev/scrape/prebuilt-parsers/instagram-post.md#post-fields), with like, comment, and view counts, paid partnerships, and sponsors. `similar_accounts` are the related profiles Instagram suggests. `business_address` is `null` unless a business account lists one.

Private profiles return their profile fields with `post_count: null` and `latest_posts: []`. Follower and following lists, business email, and phone numbers need an Instagram login and aren't returned. For a single post's comments, use [Instagram post](https://docs.context.dev/scrape/prebuilt-parsers/instagram-post.md).

## Empty results and errors

A nonexistent or removed profile produces `NOT_FOUND`. Read `parsed.success` before using the data. A failed parse has `data: null` and can coexist with successful outputs. `parsed.type` remains `"instagram-profile"` even when parsing fails. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for handling failures.

## Request options

This parser reads public Instagram data separately from the rendered page, without logging in. [Content filters](https://docs.context.dev/scrape/content-filtering.md) and [browser actions](https://docs.context.dev/scrape/browser-actions.md) do not change its results. [Browser profiles](https://docs.context.dev/scrape/browser-profiles.md) are unsupported with this parser. Other Scrape controls, including [caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), still apply.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.