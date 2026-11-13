# Pre-built parsers

> Choose a parser for Maps, app stores, Instagram, TikTok, Reddit, G2, Yelp, contact details, or links without writing CSS rules.

Use `POST /web/scrape` with `formats.parse: true`, `parseParams.type: "prebuilt"`, and one parser name per request. Don't send custom `rules`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

| Parser | Input | Data in `parsed.data` |
| - | - | - |
| [Google Maps](https://docs.context.dev/scrape/prebuilt-parsers/google-maps.md), `google-maps` | Google Maps place, search, or data URL | `results` with business records |
| [Google Maps reviews](https://docs.context.dev/scrape/prebuilt-parsers/google-maps-reviews.md), `google-maps-reviews` | Google Maps place, search, CID, or reviews URL | Up to 1,000 `reviews`, sorted newest, oldest, relevant, or by rating |
| [Google Play](https://docs.context.dev/scrape/prebuilt-parsers/google-play.md), `google-play` | Google Play app details URL | App details, ratings, downloads, and data safety |
| [Google Play reviews](https://docs.context.dev/scrape/prebuilt-parsers/google-play-reviews.md), `google-play-reviews` | Google Play app details URL | `app_id` and up to 200 recent `reviews` |
| [App Store](https://docs.context.dev/scrape/prebuilt-parsers/app-store.md), `app-store` | App Store app URL | App details, ratings, pricing, and screenshots |
| [App Store reviews](https://docs.context.dev/scrape/prebuilt-parsers/app-store-reviews.md), `app-store-reviews` | App Store app URL | `app_id` and up to 500 recent `reviews` |
| [Instagram profile](https://docs.context.dev/scrape/prebuilt-parsers/instagram-profile.md), `instagram-profile` | Instagram profile URL | Profile, stats, `similar_accounts`, and 12 `latest_posts` |
| [Instagram post](https://docs.context.dev/scrape/prebuilt-parsers/instagram-post.md), `instagram-post` | Instagram post or reel URL | Post, stats, media, and top `comments` |
| [Instagram feed](https://docs.context.dev/scrape/prebuilt-parsers/instagram-feed.md), `instagram-feed` | Instagram hashtag, keyword, or location URL | `posts` in the shared post shape |
| [TikTok profile](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-profile.md), `tiktok-profile` | TikTok profile URL | Profile, follower, like, and video counts |
| [TikTok video](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-video.md), `tiktok-video` | TikTok video or photo post URL | Post, stats, music, paid partnership, and a downloadable `video_url` |
| [TikTok feed](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-feed.md), `tiktok-feed` | TikTok profile, hashtag, or search URL | Videos in the TikTok video shape |
| [TikTok comments](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-comments.md), `tiktok-comments` | TikTok video or photo post URL | The first 20 comments, with likes, reply counts, and authors |
| [TikTok followers](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-followers.md), `tiktok-followers` and `tiktok-following` | TikTok profile URL | Followers or followed accounts in the TikTok profile shape |
| [TikTok user search](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-user-search.md), `tiktok-user-search` | TikTok user search URL | The top 10 matching accounts, with follower and like counts |
| [Reddit post](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md), `reddit-post` | Reddit post URL | `post` with media, and up to 1,000 `comments` as a nested tree |
| [Reddit search](https://docs.context.dev/scrape/prebuilt-parsers/reddit-search.md), `reddit-search` | Reddit search URL, site-wide or within one subreddit | Up to 1,000 `posts`, `communities`, or `users`, depending on the search type |
| [Reddit subreddit](https://docs.context.dev/scrape/prebuilt-parsers/reddit-subreddit.md), `reddit-subreddit` | Subreddit URL, optionally with a tab | `subreddit` details, `rules`, and up to 1,000 `posts` |
| [Reddit user](https://docs.context.dev/scrape/prebuilt-parsers/reddit-user.md), `reddit-user` | Reddit profile URL, optionally with a tab | `user` profile, `trophies`, moderated communities, and up to 1,000 `posts` and `comments` |
| [G2 reviews](https://docs.context.dev/scrape/prebuilt-parsers/g2-reviews.md), `g2-reviews` | G2 product URL | `product` and the 25 most recent `reviews`, optionally filtered by star rating |
| [Yelp search](https://docs.context.dev/scrape/prebuilt-parsers/yelp-search.md), `yelp-search` | Yelp search URL | Up to 20 ranked organic `businesses`, with total and pagination |
| [Yelp reviews](https://docs.context.dev/scrape/prebuilt-parsers/yelp-reviews.md), `yelp-reviews` | Yelp business URL | Up to 20 newest-first `reviews` per page, with business details and pagination |
| [Tripadvisor reviews](https://docs.context.dev/scrape/prebuilt-parsers/tripadvisor-reviews.md), `tripadvisor-reviews` | Tripadvisor hotel, restaurant, or attraction review URL | Up to 20 `reviews` per page, with owner responses, location details, and pagination |
| [Emails](https://docs.context.dev/scrape/prebuilt-parsers/emails.md), `emails` | Any supported page URL | `emails` with normalized contact addresses |
| [Phone numbers](https://docs.context.dev/scrape/prebuilt-parsers/phone-numbers.md), `phone-numbers` | Any supported page URL | `phone_numbers` with E.164 numbers |
| [Links](https://docs.context.dev/scrape/prebuilt-parsers/links.md), `links` | Any supported page URL | `links` with absolute URLs and text labels |

## Read the output

The `parsed` output identifies the parser in `parsed.type`. Check `parsed.success` before reading `parsed.data`; each parser’s page documents its data fields. A failed parse has `data: null`, with an `error_code` and `message`, and can coexist with successful outputs in the same request. See [timeouts and errors](https://docs.context.dev/scrape/timeouts-and-errors.md).

## Page content and browser profiles

Emails, phone numbers, and links use page HTML after [content filtering](https://docs.context.dev/scrape/content-filtering.md). They support [browser actions](https://docs.context.dev/scrape/browser-actions.md) and [browser profiles](https://docs.context.dev/scrape/browser-profiles.md). They extract from one page rather than crawling a site.

Google Maps, app store, Instagram, TikTok, Reddit, G2, and Yelp parsers fetch source data separately. Google Maps and app store parsers use a US exit; Instagram, TikTok, and Reddit parsers read public data without logging in. Content filters and browser actions do not change those parser results, and browser profiles are unsupported. Google Play’s `hl` and `gl` query parameters and the App Store’s country path still select the source locale or storefront.

[Caching](https://docs.context.dev/scrape/freshness-and-caching.md), [timeouts](https://docs.context.dev/scrape/timeouts-and-errors.md), and [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) apply to all parsers. Use the [Custom parser](https://docs.context.dev/scrape/parse-fields.md) for CSS rules or [JSON extraction](https://docs.context.dev/scrape/json.md) for a schema you define.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.