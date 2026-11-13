# Changelog

> New features, improvements, and changes that affect your integration.

Entries describe each release; linked guides document current behavior.

**November 12, 2026**

## Zero data retention for People Search and Company Search

* [People Search](https://docs.context.dev/people/search.md) and [Company Search](https://docs.context.dev/companies/search.md) now accept `zdr: "enabled"`. With ZDR on, the query and results are kept out of retained usage logs and traces, and the response includes `X-Context-ZDR: true`.
* Requires [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) to be enabled for your organization. Both playgrounds include the option.

## Developer plan back to 10,000 credits

* Every [Developer](https://docs.context.dev/account/billing.md#plan-limits) subscription now includes **10,000 credits per month** at the same \$20 price. Subscriptions started at 5,000 credits since November 7 are raised to 10,000, and 5,000 credits are added to their current balance.

**November 7, 2026**

## Developer plan and Free request limits

* New [Developer](https://docs.context.dev/account/billing.md#plan-limits) subscriptions include **5,000 credits per month**. Existing Developer subscriptions keep 10,000.
* Developer [Auto-Topup](https://docs.context.dev/account/billing.md#auto-topup-and-spend-alerts) usage is invoiced every \$10 instead of every \$100. Existing Developer subscriptions switch at their next subscription change or renewal.
* New Free organizations have a limit of **10 requests per minute** across the organization, in addition to 2 concurrent requests. Existing organizations keep their current limits. See [Rate limits](https://docs.context.dev/optimization/rate-limits.md).

**November 2, 2026**

## Social profiles in Company Search

* Each [Company Search](https://docs.context.dev/companies/search.md#read-the-results) result now includes `socials`, with the company's LinkedIn, X, Instagram, Facebook, YouTube, GitHub, Crunchbase, and Wellfound profile URLs.
* A network the company has no known profile on is `null`.

**November 1, 2026**

## Reviewer IDs in Yelp reviews

* Each review from the [Yelp reviews parser](https://docs.context.dev/scrape/prebuilt-parsers/yelp-reviews.md) now includes `author.id`, the reviewer's Yelp user ID, and `author.url`, a link to their Yelp profile.
* Use `author.id` to recognize the same reviewer across businesses and pages. Display names such as "Alex P." are often shared by many people.

**October 31, 2026**

## Ultra mode for Company Search

* Set `mode: "ultra"` on [Company Search](https://docs.context.dev/companies/search.md#choose-a-mode) for detailed requests that combine several criteria. Ultra searches more thoroughly and checks every result against each criterion in your query.
* Ultra accepts queries up to 5,000 characters and costs **10 credits** per page with results. `fast` stays the default at 2 credits and returns results in about two seconds. Ultra searches can take up to 20 seconds.
* The response shape is the same in both modes, and pages with no matches are still free.

## Reddit post parser

* Read a public Reddit post with its text, media, score, and flair, plus up to **1,000 comments** as a nested reply tree, using the [Reddit post parser](https://docs.context.dev/scrape/prebuilt-parsers/reddit-post.md).
* Order comments with the URL's `sort` parameter: `best`, `top`, `new`, `controversial`, `old`, or `qa`. Set `parseParams.limit` from 1 to 1,000 comments; the default is 100.
* Top-level comments are read before deeper replies, so a lower limit keeps whole conversations instead of one long branch.

**October 30, 2026**

## Yelp parsers

* Find businesses with the [Yelp search parser](https://docs.context.dev/scrape/prebuilt-parsers/yelp-search.md). Send a Yelp search URL and get up to 20 businesses per page in Yelp's organic order, without ads, with rating, review count, price, categories, address, coordinates, and phone.
* Read reviews with the [Yelp reviews parser](https://docs.context.dev/scrape/prebuilt-parsers/yelp-reviews.md). Send a Yelp business URL and get up to 20 reviews per page, newest first, with the full review text, rating, and reviewer details.
* Both parsers page through results with Yelp's `start` URL parameter and are available in the API and the playground.

**October 28, 2026**

## Access policies

* Control which websites your API requests can reach. An [access policy](https://docs.context.dev/optimization/access-policies.md) is an allowlist or a blocklist of domains. Each domain includes its subdomains, and `*.gov` covers a whole extension.
* List policy IDs in the new `policies` param on Scrape, Crawl, Map, Search, Answers, News, Brand, Styleguide, Prefetch, batches, and monitors. Or set `applies_to` to apply a policy automatically to chosen API keys or your whole account.
* A blocked request returns `403 ACCESS_POLICY_DENIED` and isn't charged. Search, Answers, and News remove blocked results instead. Redirects and embedded frames are checked too.
* Manage policies with the free [access policy endpoints](https://docs.context.dev/api-reference/access-policies/create.md), which use the new `access_policies:read` and `access_policies:write` [key permissions](https://docs.context.dev/account/api-keys.md). Access policies are enabled per organization; [contact us](mailto:support@context.dev) to turn them on.

## Web search monitors

* Watch the web for new developments on a topic with a [search monitor](https://docs.context.dev/monitors/targets/search.md). Each run searches your `query` and reports results you haven't seen before. Queries support operators such as `site:`, `-site:`, and quoted phrases.
* By default, an AI judge reports only results that describe a new development matching your `instructions`, and skips evergreen pages, opinion pieces, and repeats of earlier alerts. Set `change_detection.type` to `exact` to get every new result instead.
* New results arrive in the change's `matched_urls` and `evidence`. Each run costs **2 credits**. Create search monitors through the API or the dashboard.

## Zero data retention for Brand retrieval

* [Brand retrieval](https://docs.context.dev/brand/overview) now supports `zdr: "enabled"`. With ZDR on, Brand retrieval and [Styleguide](https://docs.context.dev/brand/styleguide.md) requests are kept out of logs, request-log history, and traces, and responses include `X-Context-ZDR: true`.
* Brand records and shared caches are still used, so brand data itself isn't deleted. See [Zero data retention](https://docs.context.dev/optimization/zero-data-retention.md#brand-retrieval-and-styleguide) for details.
* Requires zero data retention to be enabled for your organization. The Brand and Styleguide playgrounds include the option too.

**October 27, 2026**

## Ultra mode for People Search

* Set `mode: "ultra"` on [People Search](https://docs.context.dev/people/search.md#choose-a-mode) for detailed requests that combine several criteria. Ultra plans a deeper search, judges each candidate against every criterion in your query, and returns a `match.confidence` score from 0 to 1 with each person.
* Ultra accepts queries up to 5,000 characters and costs **50 credits** per page with results. `fast` stays the default at 10 credits. Complex ultra searches can take up to 30 seconds.
* Try both modes in the [playground](https://www.context.dev/playground/people-search).

## Page numbers in PDF Markdown

* Set `includeNumberedPages` to start each PDF page in the Markdown with a `<!-- page N -->` line that uses the page's original number, so you can cite pages or split a document by page.
* Use `includeNumberedPages=true` on [Parse](https://docs.context.dev/parse/pdfs-and-ocr.md#mark-page-numbers), or `sharedParams.parsers.pdf.includeNumberedPages` on [Scrape](https://docs.context.dev/scrape/pdfs-and-documents.md#mark-page-numbers) and batches. Scrape responses with page markers are never served from cache.
* The Parse and Scrape playgrounds have a toggle for it.

## Context.dev for Neon

* [Run Context.dev as a Neon Function](https://docs.context.dev/integrations/neon.md) from Neon's `context-dev` template, with routes for web search, scraping, Answers, Brand Retrieval, and News Search.
* Your Context.dev API key stays in the function, and callers authenticate with their own bearer token.

**October 26, 2026**

## Exact phrases in People, Company, and News search

* Put a phrase in double quotes to require it word for word in [People Search](https://docs.context.dev/people/search.md#match-exact-phrases), [Company Search](https://docs.context.dev/companies/search.md#match-exact-phrases), and natural-language [News Search](https://docs.context.dev/news/overview#match-exact-phrases).
* Join quoted phrases with `OR` to accept either one, as in `"payroll" OR "invoicing"`, and put `-` before a quoted phrase to exclude it.

**October 23, 2026**

## People Search

* [Search people](https://docs.context.dev/people/search.md) with a natural-language query, such as "VPs of sales at solar companies in California", and get up to 10 people per page with their current role and employer, location, experience, skills, schools, and profile links.
* Narrow results by country and years of experience, and page through them with a cursor.
* Each page with results costs **10 credits**; searches with no matches are free. People Search is available on all plans and in the [playground](https://www.context.dev/playground/people-search).

## New self-serve plans

New subscriptions use these monthly allowances and 1,000-credit Auto-Topup rates:

| Plan | Credits per month | Price per Auto-Topup block |
| - | -: | -: |
| Developer | 10,000 | \$3.00 |
| Pro | 100,000 | \$2.00 |
| Growth | 500,000 | \$1.50 |
| Scale | 1,000,000 | \$1.00 |
| Scale 2.5M | 2,500,000 | \$0.75 |

Existing subscriptions keep their current plan and rates. Dollar plan prices are on the [pricing page](https://www.context.dev/pricing); limits per plan are in [Plans and billing](https://docs.context.dev/account/billing.md#plan-limits).

**October 21, 2026**

## Company search

* [Search companies](https://docs.context.dev/companies/search.md) with a natural-language query and get each company's identity, headquarters, and headcount, with pagination.
* Each request costs **2 credits**; requests with no results are free.

## Research papers in Search

* [Search](https://docs.context.dev/search/overview) now includes indexed research papers for research-style queries. Papers are skipped when domain filters are set.

## Longer News descriptions

* Natural-language [News](https://docs.context.dev/news/overview#search-with-natural-language) results now return extended descriptions, combining the publisher's summary with snippets that matched your query, up to 2,000 characters.

## Choose where Markdown comes from

* Many docs sites publish a Markdown version of each page. Set `markdownParams.sourcePreference` on [Scrape](https://docs.context.dev/scrape/markdown.md#choose-the-markdown-source) and [batches](https://docs.context.dev/batches/submit.md), or `sourcePreference` on [Crawl](https://docs.context.dev/crawl/page-content.md), to rank `html-conversion` and `markdown-direct`. The first usable source wins.
* The default, `["html-conversion", "markdown-direct"]`, keeps the current behavior. Use `["markdown-direct", "html-conversion"]` to prefer the site's own Markdown, which often keeps code blocks and heading anchors cleaner.
* With only `markdown-direct`, a page that publishes no Markdown fails with `NO_PUBLISHED_MARKDOWN` and is not billed. Link and image options require `html-conversion`.
* Crawl now also falls back to published Markdown when an HTML conversion is nearly empty, as Scrape and batches already did.

## Follow only chosen languages in batch crawls

* Set `controls.languages` on a [start-URL batch crawl](https://docs.context.dev/crawl/async.md#crawl-controls) to `same_as_start_url` or a list such as `["en"]`, so translated copies of a site don't use up `maxUrls`.
* Links whose language can't be determined are still followed.

**October 20, 2026**

## No per-minute limit on Free

* New Free organizations no longer have a per-minute limit; the **2 concurrent requests** limit still applies. Existing and custom allowances are unchanged. See [Rate limits](https://docs.context.dev/optimization/rate-limits.md).

## Fewer rate-limit digests

* The daily [rate-limit digest](https://docs.context.dev/account/billing.md#account-emails) is now sent only when more than 20% of your organization's requests in the past 24 hours were rate-limited, up from 5%.

**October 19, 2026**

## Exclude URLs from crawls and site map discovery

* Skip URLs with an exclude pattern:
  * `excludeUrlRegex` on [Crawl](https://docs.context.dev/crawl/scope.md) and [Map URLs](https://docs.context.dev/map/filter-and-search.md)
  * `controls.excludeRegex` on [batch crawls](https://docs.context.dev/crawl/async.md#crawl-controls) from a start URL or sitemap.
* A URL that matches the exclude pattern is skipped even when it matches the include pattern, so you can drop sections such as `/blog/`. The start URL is always scraped.

**October 18, 2026**

## Natural-language News search

* Ask [News](https://docs.context.dev/news/overview#search-with-natural-language) in plain words, like "chip export restrictions to China", with `searchBy: { type: "natural_language", query }` and get up to **100 matching articles** ranked by relevance.
* Every News filter still applies, and the playground now opens on natural-language search.

## Credit exhaustion returns 402

* Authenticated requests rejected for insufficient credits now return **402 USAGE\_EXCEEDED**, including batch reservation failures. Previously these failures returned **401 USAGE\_EXCEEDED**. The error code and envelope fields are unchanged; clients that checked for 401 should handle 402. The public API stays on `/v1`.
* Additive [`error_data`](https://docs.context.dev/account/billing#insufficient-credits) reports known credit facts, retry conditions, and available refill information. Rejected operations remain uncharged; unknown fields are omitted.
* MCP billing failures return model-visible tool errors in text and structured content without OAuth challenges. Usage inspection remains free at zero balance. Recovery links open subscription settings; paid-feature entitlements and temporary throttling remain distinct.
* Concurrency rejections retain **429 RATE\_LIMITED** and add structured `error_data` with the effective limit, remaining slots, retry delay, zero charge, and recovery by waiting for capacity or increasing the limit. REST and MCP use `https://context.dev/dashboard/subscription` for account settings. Per-minute throttling is unchanged.

**October 17, 2026**

## TikTok parsers

* Pull TikTok profiles, videos, feeds, comments, followers, and user search results with **seven new [TikTok parsers](https://docs.context.dev/scrape/prebuilt-parsers/tiktok-profile.md)**.
* Use them through Scrape Anything or the playground, without a TikTok login. Video results include a `video_url` you can download directly.

## People Enrich on every plan

* [People Enrich](https://docs.context.dev/people/enrich.md) now works on every plan, including Free, so you can match a person from identity clues without upgrading.
* Pricing stays at 20 credits per match.

**October 16, 2026**

## Instagram parsers

* Extract public profiles, posts, reels, and hashtag, keyword, or location feeds with the three new [Instagram parsers](https://docs.context.dev/scrape/prebuilt-parsers/instagram-profile.md).
* Use them through Scrape Anything or the playground, without an Instagram login.

## Google Maps reviews

* Extract up to **1,000 reviews** for a place with the [Google Maps reviews parser](https://docs.context.dev/scrape/prebuilt-parsers/google-maps-reviews.md), in the API or playground.
* Choose newest, oldest, most relevant, highest-rated, or lowest-rated order; the default is 100 newest reviews.

## G2 reviews

* Extract the **25 most recent reviews** for a product with the [G2 reviews parser](https://docs.context.dev/scrape/prebuilt-parsers/g2-reviews.md), including ratings, reviewer details, likes, dislikes, and problems solved.
* Use it in the API or playground with optional star-rating filters in the URL; pagination is unavailable.

## Language filters for Search and News

* Set [Search](https://docs.context.dev/search/filters.md) `languages`, such as `["en", "de"]`, to narrow results by language; the default is `"all"`.
* Search and [News](https://docs.context.dev/news/filter-and-sort.md) language filters support **74 languages**; results whose language cannot be detected remain eligible.

## Brand search filters and richer results

* Filter [Brand search](https://docs.context.dev/brand/search.md) by `country` and primary `language`, such as `country=US&language=english`; both filters must match when combined.
* Results now include `description`, `country`, and `language` when available.

## Daily rate-limit digest

* Rate-limit [account emails](https://docs.context.dev/account/billing.md#account-emails) now arrive as one daily digest that names each limit you hit and exactly how many requests it rejected.
* The digest is sent only when more than 5% of your requests in the past 24 hours were rate-limited, so occasional throttling no longer fills your inbox.

**October 15, 2026**

## Scrape Anything batches up to 100,000 URLs

* Submit up to **100,000 URLs**, or crawl a site, in one asynchronous [batch](https://docs.context.dev/batches/overview).
* Combine Markdown, HTML, screenshots, images, bytes, parsers, product data, highlights, and JSON extraction with the same per-page options as [Scrape Anything](https://docs.context.dev/scrape/overview).
* Create jobs and inspect results from the dashboard too.

## List browser profiles

* [`GET /org/browser/profiles`](https://docs.context.dev/api-reference/browser-profiles/list) lists your organization's [browser profiles](https://docs.context.dev/scrape/browser-profiles.md#list-profiles) with their creation time, newest first. It costs no credits and needs `logs:read`.
* Add an optional `description` when you create a profile to label it in that list.

**October 14, 2026**

## Updated request limits

* New Free organizations receive **2 concurrent requests and 10 requests per minute**. Both limits apply across the organization.
* Existing allowances are preserved through the rollout and routine renewals. Plan changes apply the new plan's base limits; explicit overrides remain until cleared.
* The dashboard shows your effective request limits.

## Eight prebuilt parsers

* [Prebuilt parsers](https://docs.context.dev/scrape/prebuilt-parsers) extract Google Maps businesses, Google Play and App Store app details and reviews, emails, phone numbers, and links without custom extraction rules.
* Set `formats.parse: true`, `parseParams.type: "prebuilt"`, and a parser name, or choose a parser in the playground.

## Request fewer Search results

* [Search](https://docs.context.dev/search/overview) accepts `numResults` from **1–100**, down from a minimum of 10. The default remains 10.

**October 13, 2026**

## Authenticated scraping with browser profiles

* [Sign in once and reuse a saved browser session](https://docs.context.dev/scrape/browser-profiles.md) with `sharedParams.profile` on Scrape Anything. Browser profiles are available on paid plans and belong to your organization.
* Create and reuse profiles in the playground. Profile requests bypass shared caches and do not support zero data retention.

## Search understands relative time

* When you omit `freshness`, [Search](https://docs.context.dev/search/filters.md) can infer a publication window from queries such as "today" or "this week".
* An explicit `freshness` setting takes precedence.

**October 8, 2026**

## Multilingual Map search

* [Map search](https://docs.context.dev/map/filter-and-search.md#choose-pages-by-topic) matches search terms across website languages to find relevant pages even when their content uses a different language from your query.

**October 7, 2026**

## Longer batch result retention

[Batch result files](https://docs.context.dev/batches/results.md#download-files) are now kept for 180 days after the batch finishes, up from 7 days. `GET /batch/{batch_id}` returns fresh download links and `GET /batch/{batch_id}/results` serves the records for the whole window.

**October 6, 2026**

## Monthly credits for every Free organization

* [Free organizations](https://docs.context.dev/account/credits.md) receive **1,000 credits monthly**, whether they signed up with a work or personal email.

**October 5, 2026**

## Search description length

* Set `descriptionMaxCharacters` on [Search](https://docs.context.dev/search/overview#choose-what-to-return) to cap each result’s `description`.
* When it is above 0 and the query has no domain or `freshness` filter, news-index results fill that space with the article passages that best match your query.

**October 4, 2026**

## Search page reads

* [Search page reads](https://docs.context.dev/search/page-content.md#options) now default to a 20-second deadline per page, plus any `waitForMs`, instead of 45 seconds. Set `markdownOptions.timeoutOpts` to change it.
* Pages that serve an anti-bot challenge report `WEBSITE_BLOCKED` on `markdown.code` and `highlights.code`.

## JSON extraction on long pages

* [JSON extraction](https://docs.context.dev/scrape/json.md#limits) now also reads head metadata (description, canonical URL, language, author, keywords, dates), counts JSON-LD and meta tags separately from the Markdown limit, and keeps the sections that best match your schema on long pages.
* A successful extraction from a page that did not fit includes `json.isTruncated: true`.
* Numbers that do not appear on the page and punctuation-only strings are dropped from optional or nullable fields.

## Answers sources and partial answers

* [`sources`](https://docs.context.dev/answers/sources-and-deadlines) lists the pages and company or profile records read for the answer, followed by URLs cited in `json_content`.
* With `return-partial`, a model error after evidence was gathered returns a partial answer instead of failing.

## Parse and credit usage

* [Parse](https://docs.context.dev/parse/overview) returns `400 INPUT_VALIDATION_ERROR` instead of `WEBSITE_ACCESS_ERROR` for an upload it cannot read or that has no extractable content.
* [`GET /org/usage`](https://docs.context.dev/api-reference/usage/retrieve) and [`GET /org/usage/history`](https://docs.context.dev/api-reference/usage/history) return your credit balance and usage over time. They share the request logs rate limit.

**September 29, 2026**

## Product image deduplication

* Set `productParams.dedupeImages: true` to [drop visually duplicate product images](https://docs.context.dev/scrape/product.md#deduplicate-images), keeping the largest copy.
* Product adds 1 credit, with no other product surcharge.

## Removed `EXTERNAL_PROVIDER_ERROR`

* `EXTERNAL_PROVIDER_ERROR` is no longer returned. Upstream failures return `500 INTERNAL_ERROR` (Answers and People previously returned 502), failed Scrape `json` outputs report `INTERNAL_ERROR`, and Answers time limits return `504 REQUEST_TIMEOUT`.

## Longer Search cache windows

* [Search Markdown](https://docs.context.dev/search/page-content.md#options) now defaults `maxAgeMs` to 180 days (`15552000000` ms), or 365 days when only highlights are requested.

**September 28, 2026**

## Highlights on Search

* [Search](https://docs.context.dev/search/page-content.md) returns passages relevant to your query with `highlightsOptions.enabled`. Each result reports `highlights.code`, like `markdown.code`.
* Search Markdown and highlights each add 1 credit per 10 results when at least one result returns them.
* **Superseded October 9:** Markdown now adds 1 credit per result returned with Markdown; see [current Search pricing](https://docs.context.dev/account/credits.md).
* Search Markdown now defaults `maxAgeMs` to 15 days (`1296000000` ms).
* [Scrape highlights](https://docs.context.dev/scrape/highlights.md) now add 1 credit instead of 3.

**September 27, 2026**

## Concurrency limits

New organizations are limited by concurrent requests instead of requests per minute: Free 1, Developer 10, Pro 100, Growth 250, and Scale 500. The limit applies across the organization and to every API key. Organizations created earlier keep their per-minute limits. Concurrency responses include `X-RateLimit-Mode: concurrency` and omit `X-RateLimit-Reset`. See [Rate limits](https://docs.context.dev/optimization/rate-limits.md).

**Superseded October 14:** new Free organizations get 2 concurrent requests; see [Plan limits](https://docs.context.dev/account/billing.md#plan-limits).

## Browser actions on page monitors

[Page monitors](https://docs.context.dev/monitors/targets/page.md) accept `target.actions`, up to 5 [browser actions](https://docs.context.dev/scrape/browser-actions.md) that run before each capture. Actions require a paid plan, and each run with actions costs 2 credits.

## Longer scrape cache windows

[Scrape](https://docs.context.dev/scrape/freshness-and-caching.md) and [batch page options](https://docs.context.dev/batches/submit.md#per-page-options) now default `maxAgeMs` to three days (`259200000` ms) and accept up to 365 days (`31536000000` ms). Set `0` to fetch fresh content. The synchronous Crawl cache window is unchanged.

**September 26, 2026**

## Answers page caching

* [Answers](https://docs.context.dev/answers/sources-and-deadlines.md#freshness) can reuse cached page reads: up to 30 days old in `fast` and 7 days in `ultra`.

## Plan changes and account limits

* Upgrades take effect immediately and preserve your remaining credits. Downgrades take effect at renewal and can be cancelled beforehand.
* Review [billing](https://docs.context.dev/account/billing.md) for plan changes, Auto-Topup, and spend alerts.
* Rate-limit reminder emails help you identify sustained throttling.
* Free organizations receive an email when repeated errors disable their keys. [Fix failing requests](https://docs.context.dev/optimization/troubleshooting.md) and contact support before resuming traffic.

## Agent Feedback

* Agents can [report problems](https://docs.context.dev/optimization/agent-feedback.md) with API calls, documentation, SDKs, or the CLI.
* Include a category, a short note, and the affected request ID or URL.
* [Submit feedback](https://docs.context.dev/api-reference/feedback/submit.md) with any API key, at no credit cost.

**September 23, 2026**

## Auto-Topup in smaller blocks

New subscriptions use **1,000-credit Auto-Topup blocks**:

| Plan | Price per block |
| - | - |
| Developer | \$2.20 |
| Pro | \$1.80 |
| Growth | \$1.40 |
| Scale | \$1.00 |

Existing subscriptions keep their current rates.

[Manage Auto-Topup and spend alerts](https://docs.context.dev/account/billing.md#auto-topup-and-spend-alerts).

## Highlights format on Scrape

* [Find the passages most relevant to a question or topic](https://docs.context.dev/scrape/highlights.md) with `formats.highlights` and `highlightsParams.query`.
* Set `maxCharacters` to limit the total length. Highlights also work with [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md).
* Adds 3 credits only when passages are returned.

## Extract product data with scrape

* [Extract product details](https://docs.context.dev/scrape/product.md) with `formats.product`, including prices, images, and variants.
* Results identify whether the URL is a product page and include a normalized product record when available.
* Adds 1 credit.

**September 22, 2026**

## Scrape Anything

* [Scrape a page once](https://docs.context.dev/scrape/overview) for Markdown, HTML, screenshots, images, original bytes, or selected fields. Choose any combination with `formats`.
* Control freshness with `maxAgeMs`; use `0` to fetch fresh content.
* Costs 1 credit, or 2 with browser actions, plus 1 per PDF page recovered by OCR.

## Map website URLs

* [Discover a site's URLs](https://docs.context.dev/map/overview) with available titles, descriptions, keywords, and languages.
* Filter and search the list, include subdomains, or set a maximum number of links.
* Costs 1 credit, or 2 when using `search`.

## SDK updates

* All five [SDKs](https://docs.context.dev/sdks) now support Scrape and Map URLs.
* Replace the old per-format scraping methods with the unified [Scrape](https://docs.context.dev/scrape/overview) and [Map](https://docs.context.dev/map/overview) methods.
* Existing HTTP routes keep working. The [CLI](https://docs.context.dev/install-cli.md) does not yet include these two commands.

**September 20, 2026**

## Bytes with rendering and cache controls

* [Download rendered HTML bytes](https://docs.context.dev/scrape/bytes.md) after a `waitForMs` delay. Other resources keep their original bytes.
* Downloads are cached for one day by default, up to 30 days. Use `maxAgeMs=0` to fetch fresh content.
* **Superseded September 27:** the cache window now defaults to three days, up to 365 days; see [Freshness and caching](https://docs.context.dev/scrape/freshness-and-caching.md).
* Requests with credentials or zero data retention bypass caching.

## Screenshots with custom headers

* Send [custom target headers](https://docs.context.dev/scrape/location-and-headers.md#target-headers), including authorized cookies, when taking screenshots.
* Requests with custom headers bypass caching and return an inline PNG data URL.

## Country routing for page images

* Use `country` to [extract page images from a selected region](https://docs.context.dev/scrape/location-and-headers.md#country).
* The country applies to both the page and its image downloads.

**September 18, 2026**

## SOC 2 Type II compliance

* Context.dev is now SOC 2 Type II compliant.
* Review security policies, subprocessors, and access to compliance evidence in the [Trust Center](https://trust.context.dev/).

## Screenshots from a full URL

* Capture a page from its full URL with [`GET /web/scrape/screenshot`](https://docs.context.dev/scrape/screenshot), for 1 credit.
* See the [screenshot guide](https://docs.context.dev/scrape/screenshot.md) for capture options and examples.
* **Superseded September 22:** capture screenshots with `formats.screenshot` on [Scrape](https://docs.context.dev/scrape/screenshot.md).

## Extract fields with CSS

* Use CSS selectors to return structured fields alongside a page's HTML, with no additional credits.
* [`extractRules`](https://docs.context.dev/scrape/parse-fields) supports text, attributes, lists, and nested objects.
* **Superseded September 22:** use `formats.parse` with `parseParams.rules` on [Scrape](https://docs.context.dev/scrape/parse-fields.md).

## Zero data retention for AI endpoints

* [Zero data retention](https://docs.context.dev/optimization/zero-data-retention.md) now supports Answers, Search, People Enrich, Images, and Styleguide.
* Enable it for your organization, send `zdr: "enabled"`, and verify `X-Context-ZDR: true` on supported requests.

## API keys during onboarding

* [Onboarding](https://docs.context.dev/quickstart.md) now picks up newly created API keys without getting stuck waiting.
* If loading fails, you can retry; setup prompts become copyable once the key is ready.

## More reliable scraping and API errors

* Pages with large response headers can now be scraped.
* Temporary gateway failures return a JSON `503` response. See [troubleshooting](https://docs.context.dev/optimization/troubleshooting.md) for recovery guidance.

**September 17, 2026**

## More reliable payments

* Fixed duplicate Auto-Topup charges when several requests reach a low balance together.
* [Plan upgrades](https://docs.context.dev/account/billing.md#change-a-plan) also wait for successful payment, with a clear recovery path when payment fails.

## Startup and nonprofit program

* Eligible startups and registered nonprofits can [apply for 30% off their first year](https://www.context.dev/startups) on a self-serve annual paid plan, with a private Slack Connect channel.
* Approval is required; overages are excluded, and existing agreements stay unchanged.

**September 16, 2026**

## Reinforcement learning grants

* Teams building reinforcement learning systems can now [apply for Context.dev data credits](https://www.context.dev/rl-grants).
* The program page explains eligibility and how to submit a research proposal.

**September 15, 2026**

## Timeout controls and partial results

* Set a [request deadline](https://docs.context.dev/optimization/timeouts.md) and choose whether to fail or accept partial results with `timeoutOpts`.
* Partial results are marked with `partial: true` or `finalDOMState: "still-loading"`. Bytes and Prefetch support fail behavior only.
* **September 16 update:** partial HTML, Markdown, Images, Screenshot, and Styleguide captures accept budgets from 5,000 ms.

## Download raw resource bytes

* [Download images, PDFs, HTML, and other resources](https://docs.context.dev/scrape/bytes.md) as base64, with file size, content type, final URL, and origin status.
* Supports files up to 20 MiB, custom headers, country targeting, and zero data retention.
* Costs 1 credit per download.

## Parse documents up to 50 MiB

* [Parse](https://docs.context.dev/parse/overview) now accepts uploads up to **50 MiB**, twice the previous limit.
* Conversion remains 1 credit, plus 1 credit per PDF page recovered by optional OCR.

## Request logs and search results

* [Request logs](https://docs.context.dev/optimization/usage-and-logs.md) redact recognized credentials in request fields, headers, and URLs.
* [Web Search](https://docs.context.dev/search/overview) results always include a `description` string, empty when no snippet is available.

**September 14, 2026**

## Advanced monitor controls

* Focus [page monitors](https://docs.context.dev/monitors/targets/page.md) on specific content with include and exclude selectors.
* Changing filters starts a new baseline. Empty filtered results fail the run and preserve the previous baseline.
* The dashboard adds controls for whitespace, webhook retries, and extraction depth.

**September 12, 2026**

## Answers: web research in two modes

* [Ask a question about the live web](https://docs.context.dev/answers/overview) and receive JSON with source URLs.
* **Fast:** 10 credits with a 30-second budget. **Ultra:** 100 credits with a 50-second budget.
* The API defaults to Ultra; the playground defaults to Fast.

## Restricted API keys and per-key usage

* [Restricted API keys](https://docs.context.dev/account/api-keys.md) let you grant only the data, log, monitor, and batch access an integration needs.
* Existing keys keep full access.
* Search and filter keys, then open their usage charts and request logs from the dashboard.

## Team roles and deactivation

* Manage [Owner, Admin, and Member roles](https://docs.context.dev/account/team.md), transfer ownership, and deactivate or reactivate teammates.
* Deactivation revokes the person's credentials and prevents invitations or domain auto-join from restoring access.

## Formatted Slack webhook notifications

* Send [monitor](https://docs.context.dev/webhooks.md#configure-delivery) and [batch](https://docs.context.dev/webhooks.md#configure-delivery) events directly to Slack or GovSlack for readable messages with resource links.
* Other webhook destinations continue receiving JSON.

## More accurate freshness controls

* Brand retrieval and Styleguide now honor `maxAgeMs: 0` and values under one day.
* Set `0` to fetch fresh data.
* The three-month default and one-year maximum are unchanged.
* See [Cache freshness](https://docs.context.dev/optimization/best-practices.md#set-cache-freshness).

**September 11, 2026**

## Updated Free credit allowances

* [Free organizations](https://docs.context.dev/account/credits.md) with a work email now receive **1,000 credits monthly**.
* Personal-email organizations receive **250 credits once**, without monthly refills.
* This replaces the September 6 allowance.
* **Superseded October 6:** see [current Free credits](https://docs.context.dev/account/credits.md).

## Request log endpoints

* [Find requests](https://docs.context.dev/api-reference/logs/list.md) by time, endpoint, key, status, error, or tags, and [retrieve an individual call](https://docs.context.dev/api-reference/logs/retrieve.md).
* Responses now include `request_id` and `X-Request-Id` for tracing.
* Log endpoints cost 0 credits.

## Better blocked-page detection

* Scraping now recognizes more CAPTCHA, login, and access-denied pages, including pages that return HTTP `200`.
* These return `WEBSITE_BLOCKED` instead of being billed and cached as usable content.
* Brand cache metadata also reflects the age of the underlying scrape more accurately.

**September 8, 2026**

## Context.dev for Gemini CLI

* [Connect Gemini CLI](https://docs.context.dev/integrations/gemini-cli.md) to search, scrape, extract, parse, and retrieve brand data from the terminal.
* The official extension uses browser-based OAuth.

## Context.dev for Composio

* [Use Context.dev through Composio](https://docs.context.dev/integrations/composio.md) for scraping, extraction, parsing, brand data, batches, and monitors.
* Connect an API key to make the toolkit available to your agent framework.

**September 7, 2026**

## Context.dev for Replit

* [Connect Context.dev to Replit Agent](https://docs.context.dev/integrations/replit.md) to search, scrape, and retrieve company data while building your app.

## Webhook retries, delivery history, and replay

* Configure [automatic webhook retries](https://docs.context.dev/webhooks.md) for batches and monitors with `webhook.retry`.
* [Replay failed deliveries](https://docs.context.dev/api-reference/webhooks/retry.md) for up to seven days, without rerunning the job or spending credits.
* Inspect 30 days of delivery history and attempts in the dashboard.

**September 6, 2026**

## Monthly API credits for new Free accounts

* New Free accounts received monthly allowances of 500 credits with a work email or 250 with a personal email.
* Refills preserved balances above the allowance.
* **Superseded September 11:** see [current Free credits](https://docs.context.dev/account/credits.md).

## Higher default monitor limits

* [Monitor allowances](https://docs.context.dev/monitors/limits-and-errors.md) increase from 2 to **10** on Free, 50 to **100** on Developer, and 500 to **1,000** on Pro.
* Scale's default is **10,000** monitors.

## More reliable brand profiles and SVG logos

* [Brand retrieval](https://docs.context.dev/brand/overview) handles redirects, placeholder sites, and error pages more accurately.
* SVG logos now render more reliably outside the original website.

## Clearer credit counters and dashboard support

* [Dashboard counters](https://docs.context.dev/optimization/usage-and-logs.md) distinguish monthly allowances from bonus balances, and Support chat is available after onboarding.
* Monthly refills also preserve manually granted balances above the allowance.

**September 4, 2026**

## Zapier 3.1

* [Zapier 3.1](https://docs.context.dev/nocode/zapier.md) adds event triggers and actions across scraping, extraction, batches, monitors, and brand data.
* Start a Zap from a website change, monitor run, or finished batch.
* Existing 3.0 Zaps keep running.

**September 3, 2026**

## Downloadable captured font files

* Styleguide now returns captured font files through stable CDN URLs in `fontLinks`, so downloads work outside the source website.
* See [Extract a design system](https://docs.context.dev/brand/styleguide.md).

## More playground languages

* The playground's [language selector](https://docs.context.dev/search/filters.md) now includes all 120 languages supported by the API, plus automatic detection.

## Better crawls of redirected documentation sites

* [Crawl](https://docs.context.dev/crawl/overview) follows sites that redirect to a dedicated documentation subdomain and continues beyond the first page more reliably.

## Context.dev on Zapier

* Connect Context.dev to your other apps with the [Zapier integration](https://docs.context.dev/nocode/zapier.md).
* The guide includes setup, available actions, and automation recipes.

## URL mapping can include subdomains

* Set `includeSubdomains: true` to [discover URLs](https://docs.context.dev/map/overview) across a domain and its public subdomains.
* The default remains `false`; the option is also available in the playground.

**September 2, 2026**

## Enterprise SSO on the Scale plan

* Scale organizations can [connect an identity provider](https://docs.context.dev/account/team.md#invitations-and-sso) from Organization Settings.
* Owners create a setup link valid for 24 hours.
* Verified company-domain teammates are routed to the provider at sign-in. Password sign-in remains available.

**September 1, 2026**

## Create additional organizations

* Use the [dashboard's organization switcher](https://context.dev/dashboard) to create another organization when every organization you own is on a paid plan.
* Each has separate members, API keys, and billing.

**August 27, 2026**

## Cache metadata on every cacheable response

* [Cacheable responses](https://docs.context.dev/scrape/freshness-and-caching.md) now include `cache_metadata` with a `hit`, `miss`, or `zdr` status and `age_ms`, so your application can see how fresh the data is.

**August 26, 2026**

## Context.dev for Claude

* [Connect Context.dev to Claude](https://docs.context.dev/integrations/claude-connector.md) from the Connectors Directory to search, scrape, crawl, extract, parse, and monitor the web.

## Dashboard dark mode

* Choose light, dark, or system appearance from the [dashboard user menu](https://context.dev/dashboard).
* Your preference is remembered across visits.

## More reliable slow-page scraping

* [Slow-loading pages](https://docs.context.dev/scrape/waiting-and-rendering.md) have more time to finish browser rendering, and repeat scrapes can reuse a working access route for sites with stricter protection.

**August 25, 2026**

## Pause your plan for up to three months

* [Pause a paid plan](https://docs.context.dev/account/billing.md#pause-or-cancel) for one, two, or three months, starting at renewal.
* Monthly charges, included-credit allocations, and Auto-Topup pause. Existing credits remain usable.
* Cancel a scheduled pause, or pay to resume early and restore monthly credits.

## Office documents with incorrect content types

* [Word, Excel, and PowerPoint files](https://docs.context.dev/parse/formats.md) served with incorrect content types are now recognized and parsed instead of being treated as webpage HTML.

**August 24, 2026**

## Timestamped YouTube transcripts

* [YouTube transcripts](https://docs.context.dev/scrape/youtube.md) now include timestamps roughly every 30 seconds, making it easier to trace a passage back to the video.

## Payment alerts and plan status

* Organization owners now receive an email when a subscription payment fails, with a link to [update the payment method](https://docs.context.dev/account/billing.md).
* The dashboard also shows scheduled cancellations.

## Website names in batch lists

* [Batch lists](https://docs.context.dev/batches/results.md) now show each job's target website, making similar jobs easier to distinguish.

**August 23, 2026**

## Scroll pages before scraping

* [Browser actions](https://docs.context.dev/scrape/browser-actions.md) now support scrolling to load more content before capturing Markdown, HTML, or Images.
* Scroll controls are also available in the playground.

## Duplicate monitors in one click

* Choose **[Duplicate](https://docs.context.dev/monitors/overview)** from a monitor's menu to open a new monitor with the same settings.
* Change the target and save.

## Email verification survives mail scanners

* Verification links now wait for your confirmation, preventing email security scanners from consuming them before you open them.
* This applies to signup and account-email changes.

**August 22, 2026**

## Logo Link wordmarks

* [Logo Link](https://docs.context.dev/brand/logo-link.md) now accepts `type=wordmark` to prefer wide wordmarks over square icons.
* Combine it with `theme=light` or `theme=dark`.

## Richer playground results

* [Playground](https://context.dev/dashboard) results now show page metadata, freshness, and browser-action outcomes, with clearer previews for scrape, extract, brand, and parse requests.
* Parse displays its OCR credit cost before you run it.

**August 21, 2026**

## Context.dev for ChatGPT

* [Add Context.dev to ChatGPT](https://docs.context.dev/integrations/chatgpt-plugin.md) to search, scrape, crawl, extract, parse, and monitor the web from a conversation.

**August 20, 2026**

## Website privacy controls

* Choose which analytics cookies to allow through the website's consent controls.
* Optional analytics wait for your consent.

**August 19, 2026**

## Context.dev for Cursor

* [Install the Cursor plugin](https://docs.context.dev/integrations/cursor-plugin.md) to give your coding agent access to Context.dev's web tools.

**August 18, 2026**

## Context.dev for LangChain

* Use [LangChain's Context.dev integration](https://docs.context.dev/integrations/langchain.md) for search, scraping, extraction, parsing, brand data, monitors, and batches.
* Install the `langchain-context` package to get started.

**August 17, 2026**

## Clear obstructive popups from screenshots

* Set `clearPopups=true` to dismiss obstructive banners, popups, and overlays before [taking a screenshot](https://docs.context.dev/scrape/screenshot.md).
* **Superseded September 22:** use `sharedParams.dismissPopups` on [Scrape](https://docs.context.dev/scrape/screenshot.md).

## Context.dev for OpenClaw

* [Connect OpenClaw](https://docs.context.dev/integrations/openclaw.md) for web search and scraping, with optional OAuth access to Context.dev's public MCP tools.

## Exclude more domains from web search

* [Web Search](https://docs.context.dev/api-reference/web-scraping/search.md) now accepts up to 100 excluded domains, giving you more control over which sources appear in results.

## More accurate brand colors, logos, and contacts

* [Brand profiles](https://docs.context.dev/brand/overview) better match website colors, preserve original logos, and filter placeholder contact emails.
* Redirects to shared hosting platforms no longer replace the requested company's brand with the platform's.

**August 16, 2026**

## News Search launches in beta

* [Find company news](https://docs.context.dev/news/overview) by name, domain, ticker, or ISIN.
* Filter by publisher, date, article type, language, or country.
* Successful searches cost 1 credit per 10 returned articles. A successful search with no articles is free.

## More control over Brand Search matching

* [Brand Search](https://docs.context.dev/api-reference/brand-intelligence/search.md) adds `autocomplete`, `queryBy`, and `typoTolerance`.
* Choose name or domain matching, prefix matching, and tolerance for up to two typos.
* These controls are also in the playground.

**August 14, 2026**

## Change your account email securely

* Change your email from Personal Settings after confirming your identity and verifying the new address.
* Your previous address receives a notification, and you stay signed in.

**August 13, 2026**

## Context.dev for Eve

* [Add Context.dev to Eve](https://docs.context.dev/integrations/eve.md) with `eve add connection/context` for search, scraping, extraction, and brand tools.
* Each user authorizes their account in the browser.

**August 12, 2026**

## Screenshots now cost 1 credit

* Screenshot requests now cost **1 credit**.
* See [Take a screenshot](https://docs.context.dev/scrape/screenshot.md) for capture options and examples.

## Earn extra credits

* Eligible Free accounts with a personal email can [earn bonus credits](https://docs.context.dev/account/credits.md#free-balance-and-refills) by following Context.dev or submitting a public post for review.
* The dashboard shows the available rewards and submission status.

## Better text encoding

* Pages, feeds, and sitemaps now respect declared character encodings, reducing garbled text on sites that use older encodings.

**August 10, 2026**

## Prefetch styleguides ahead of time

* Queue a styleguide with `type: "styleguide"` on [Prefetch](https://docs.context.dev/brand/prefetching.md) to reduce the wait for a later Styleguide request.
* Prefetching costs 0 credits.

**August 9, 2026**

## HTML alongside Markdown in one scrape

* Set `includeHTML=true` to [return HTML and Markdown together](https://docs.context.dev/scrape/overview) from one scrape.

**August 7, 2026**

## Page headings and main content

* HTML and Markdown responses now include `metadata.headings` in document order for tables of contents and content routing.
* [Main-content filtering](https://docs.context.dev/scrape/content-filtering.md) also preserves the page's `<main>` landmark.

**August 6, 2026**

## People Enrichment API

* [Find a person](https://docs.context.dev/people/enrich.md) from a social URL, name and company, or work email, with a 0–100 match score.
* The beta is available on paid plans and costs 20 credits per successful match.
* Free and disposable email inputs are rejected without charge.

## Employee counts on brand data

* [Brand profiles](https://docs.context.dev/brand/overview) now include `employees` with a headcount range and an exact count when known.
* Unknown values are `null`.

## Relevance search for URL mapping

* Give [Map URLs](https://docs.context.dev/map/overview) a `search` phrase such as `pricing and plans` to return matching pages in relevance order.
* Searched requests cost 2 credits instead of 1.

## Per-page OCR billing and clearer PDF errors

* OCR adds 1 credit per recovered PDF page to the 1-credit request cost.
* [Enable OCR](https://docs.context.dev/parse/pdfs-and-ocr.md) with `ocr=true` for Parse or `pdf[ocr]=true` for scraping.
* Image-only PDFs return `PDF_IMAGES_ONLY` when OCR is needed.

## Clearer timeouts for new brand lookups

* A brand lookup on a new domain with a timeout below 10 seconds now returns `422 COLD_DOMAIN_TIMEOUT_TOO_LOW` immediately.
* Timeout responses suggest [prefetching](https://docs.context.dev/brand/prefetching.md) the brand before you need it.

## YouTube pages become structured Markdown

* [Scrape a YouTube video or channel](https://docs.context.dev/scrape/youtube.md) to receive its available metadata and description as structured Markdown.
* Videos with retrievable captions also include a transcript.

**August 5, 2026**

## More specific scrape errors

* [Identify scrape failures](https://docs.context.dev/optimization/troubleshooting.md) with clearer errors for oversized content, unresolved domains, and intentionally skipped PDFs.
* Oversized embedded files no longer fail the entire page scrape.

## Faster repeat scrapes

* [Repeat scrapes](https://docs.context.dev/scrape/freshness-and-caching.md) of unchanged pages return faster by reusing the previous Markdown conversion.

**August 4, 2026**

## Brand Search for autocomplete

* [Find up to 10 matching companies](https://docs.context.dev/brand/search.md) by name or domain, with logos for autocomplete and lookup forms.
* At launch, requests are free on Pro and Scale and cost 1 credit on Free and Starter.
* **August 6 update:** name matches rank first, and Brand Search is available in the playground.

**August 3, 2026**

## Context.dev MCP is live

* [Connect your AI client over MCP](https://docs.context.dev/install-mcp.md) to use Context.dev through browser-based OAuth.
* Setup guides cover Claude, Claude Code, Cursor, Codex, ChatGPT, and VS Code.

**August 2, 2026**

## Usage charts by product

* [Dashboard usage charts](https://docs.context.dev/optimization/usage-and-logs.md) now separate All, Data APIs, Monitors, and Batches, so you can track activity by product.

## Monitors recover from failed runs

* [Monitors](https://docs.context.dev/monitors/limits-and-errors.md) recover from temporary scraping failures instead of pausing after one failed run.
* Resume an already paused monitor by setting its status to `active`.

**August 1, 2026**

## Credit refills on your billing day

* [Monthly credits](https://docs.context.dev/account/billing.md#refills) now refill on your billing day, including monthly allocations on annual plans.
* Your allowance covers a full cycle from subscription rather than resetting on the first of the calendar month.
* Auto-Topup preferences are also preserved across plan changes.

**July 30, 2026**

## Batch scraping for up to 25,000 URLs

* [Scrape up to 25,000 URLs asynchronously](https://docs.context.dev/batches/overview), using a list, a starting page, or a sitemap.
* Get results through polling, webhooks, or downloads.
* Credits are reserved for the accepted page budget. Only successful pages are charged; unused credits are released.
* Use item IDs and idempotency keys to match results and retry submissions safely.
* **Superseded October 15:** batches now accept up to 100,000 URLs with [Scrape Anything](https://docs.context.dev/batches/submit.md) formats.

## Connect AI agents over MCP with OAuth

* [Connect an AI client over MCP](https://docs.context.dev/install-mcp.md) and authorize it in your browser with OAuth.
* The consent screen identifies the client and requested access; no API key needs to be pasted into its configuration.

**July 27, 2026**

## Monitor the changes that matter

* Give [page monitors](https://docs.context.dev/monitors/targets/page.md) instructions describing which changes matter, such as pricing changes rather than rotating testimonials.
* Semantic detection filters irrelevant changes; empty or blocked snapshots fail the run without replacing a valid baseline.

**July 25, 2026**

## Usage alerts for overages

* Set an [Auto-Topup budget](https://docs.context.dev/account/billing.md#auto-topup-and-spend-alerts) and receive email alerts at selected spending thresholds.
* Alerts are a soft cap: API requests, monitors, and Auto-Topup continue after the budget is exceeded.

**July 22, 2026**

## Simpler monitor setup and secret rotation

* [Create a monitor](https://docs.context.dev/monitors/overview) with just `name` and `target`. Scheduling defaults to daily, with detection selected for the target.
* Check the baseline run using `initial_run_id`.
* [Rotate webhook signing secrets](https://docs.context.dev/api-reference/monitors/rotate-webhook-secret.md) without replacing the monitor. The old secret stops signing new deliveries immediately.

## Browser actions before scraping

* [Click, type, or wait](https://docs.context.dev/scrape/browser-actions.md) before scraping Markdown, HTML, or Images. Paid plans support up to five ordered actions.
* Standard requests with actions cost 2 credits and bypass caching. Enriched image requests remain 5 credits.

**July 21, 2026**

## Zero data retention

* Eligible scraping and parsing requests now support [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md).
* Set `zdr=enabled` to bypass shared caches and retained content logs, and verify the `X-Context-ZDR: true` response header.

**July 20, 2026**

## Default organization

* Choose which [organization](https://docs.context.dev/account/team.md) opens by default when you use more than one account workspace.

**July 18, 2026**

## Layout-aware PDF parsing

* [Parse PDFs](https://docs.context.dev/parse/pdfs-and-ocr.md) with better tables, reading order, headings, and subscript or superscript text.
* Display equations are preserved as text. OCR can also recover corrupted text layers.
* This update applies to Parse. See the guide for current OCR controls and billing.

**July 17, 2026**

## Faster web dashboard

* [Dashboard](https://context.dev/dashboard) pages load faster when moving between usage, API keys, team settings, and product views.

**July 12, 2026**

## Request tags for usage tracking

* [Tag requests](https://docs.context.dev/optimization/usage-and-logs.md) by customer, feature, or environment, then filter charts and logs by those tags.
* Add up to 20 labels without changing pricing or caching. Monitor resource tags remain separate.

## Parse file bytes to Markdown

* [Upload documents directly](https://docs.context.dev/parse/overview) and get Markdown without hosting a file at a URL.
* Choose format hints, PDF page ranges, and content controls. Conversion costs 1 credit, with optional OCR charges.
* The launch limit is 25 MiB, increased to **50 MiB** on September 15.

**July 11, 2026**

## Rate-limit headers on every response

* Authenticated responses now include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset`, so you can pace calls before hitting the limit.
* A `429` also includes `Retry-After`.
* See [Rate limits](https://docs.context.dev/optimization/rate-limits.md).

## Cleaner main-content Markdown

* Main-content filtering removes more navigation, ads, comments, and layout markup from [Markdown scrapes](https://docs.context.dev/scrape/overview).
* The response also includes `contentLength`, measured in UTF-8 bytes, to help detect empty results.

## Per-run monitor webhooks

* Subscribe to [`run.completed`](https://docs.context.dev/monitors/webhooks) for a signed webhook after every completed run, including baseline and no-change runs.
* Existing integrations continue receiving `change.detected` only.
* Run history adds `webhook_deliveries`. The singular field remains available but is deprecated.

## Monitor webhook health tracking

* Receive an email after three consecutive monitor runs with failed webhook deliveries.
* A successful delivery or webhook URL change clears the failure streak. Rate-limited receivers are retried using `Retry-After`.
* See [delivery failures](https://docs.context.dev/monitors/webhooks.md#delivery-failures) for recovery steps.

**July 10, 2026**

## Join an organization by email domain

* Let teammates with a verified company email domain discover and [join your organization](https://docs.context.dev/account/team.md#invitations-and-sso) without an invitation.
* Manage the setting from the dashboard.

**July 9, 2026**

## Website monitors

* [Watch a page, sitemap, or structured data](https://docs.context.dev/monitors/overview) on a schedule and receive signed webhooks when it changes.
* Manage monitors, runs, and changes through the API or SDKs, at no credit cost.
* Successful page and sitemap checks cost 1 credit; extract checks cost 10. Failed or skipped runs are free.

**July 7, 2026**

## Brand lookup from an exact URL

* [Retrieve brand data from an exact page](https://docs.context.dev/brand/lookup-by-url.md) with `type: "by_direct_url"`.
* Results use that page's content only and cost 10 credits on success.
* Domain-lookup options such as `maxSpeed`, `force_language`, and `maxAgeMs` are not supported.

**July 5, 2026**

## One request for brand lookups

* Use one [`POST /brand/retrieve`](https://docs.context.dev/api-reference/brand-intelligence/brand) operation for domain, email, name, ticker, and transaction lookups.
* The `type` field selects the lookup, giving SDK integrations one consistent entry point.

## One request for prefetching

* [Prefetch](https://docs.context.dev/brand/prefetching.md) now uses one request with a `type` field for queuing brand data by domain or email.

## API reference navigation

* The [API reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) now groups related operations, uses shorter names, and redirects legacy pages to their replacements.

**July 4, 2026**

## Customer referrals

* Share your referral link from the dashboard.
* Referred customers receive 10% off for 12 months, and you earn 10% of their payments for a year.
* The program is available to existing customers without an application and is separate from the affiliate program.

## Remove duplicate images

* Set `dedupe=true` on [Images](https://docs.context.dev/scrape/images.md) to remove near-duplicate images without changing the request price.
* **Superseded September 22:** use `imageParams.dedupe: "visual"` on [Scrape](https://docs.context.dev/scrape/images.md#enrich-and-deduplicate).

## Scrape PowerPoint presentations

* [Scrape PowerPoint URLs](https://docs.context.dev/scrape/pdfs-and-documents.md) into Markdown or HTML, including slide text, tables, and speaker notes.
* Supports PPTX and legacy PPT. Crawls can follow links to presentations.

**July 3, 2026**

## Scrape spreadsheets and CSV files

* Scrape [Excel and CSV URLs](https://docs.context.dev/scrape/pdfs-and-documents.md) into tables.
* Workbooks return separate sheet tables, and CSV output preserves an optional title or attribution above the header.
* Markdown, HTML, and Crawl support the new formats.

**July 2, 2026**

## #1 Product of the Day on Product Hunt

* Context.dev reached [#1 Product of the Day on Product Hunt](https://www.producthunt.com/products/context-dev).
* Thank you for the feedback and support.

**June 29, 2026**

## Logo Link themes

* Choose `theme=light` or `theme=dark` on [Logo Link](https://docs.context.dev/brand/logo-link.md) to prefer a matching logo variant.
* Without a theme, the highest-resolution available logo remains the default.

## Settle animations before capture

* Set `settleAnimations=true` to [stabilize animations](https://docs.context.dev/scrape/waiting-and-rendering.md) before capturing HTML, Markdown, or crawled pages.
* The option defaults to `false`.

**June 27, 2026**

## Capture light and dark themes

* Set `colorScheme` to `light` or `dark` when [taking screenshots](https://docs.context.dev/scrape/screenshot.md) or [extracting a styleguide](https://docs.context.dev/brand/styleguide.md) to capture the site's selected color mode.
* **Superseded September 22:** screenshots now use `sharedParams.theme` on [Scrape](https://docs.context.dev/scrape/screenshot.md); Styleguide keeps `colorScheme`.

## Dashboard refresh

* The refreshed [dashboard](https://context.dev/dashboard) brings consistent navigation across signup, overview, team management, and API tools, with clearer parameter controls and usage displays.

**June 26, 2026**

## Scrape from a selected country

* Fetch supported scraping, crawling, and screenshot requests from a [selected country](https://docs.context.dev/scrape/location-and-headers.md#country) using a two-letter `country` code.
* Use it when page content or access varies by location.

**June 24, 2026**

## Capture sections of long pages

* Use `scrollOffset` to capture a viewport-sized section of a long page starting at a selected vertical offset.
* See [Take a screenshot](https://docs.context.dev/scrape/screenshot.md).
* **Superseded September 22:** set a rectangle in `screenshotParams.area` on [Scrape](https://docs.context.dev/scrape/screenshot.md#choose-the-area-and-format).

**June 23, 2026**

## Annual plans

* Annual billing is now available with two months free compared with monthly billing.
* Choose yearly billing on the [pricing page](https://www.context.dev/pricing).

**June 22, 2026**

## Account setup for coding agents

* Coding agents can start account setup through [auth.md](https://context.dev/auth.md).
* Follow the browser verification step to claim the account and complete setup.

**June 21, 2026**

## PHP SDK

* The official [PHP SDK](https://docs.context.dev/sdks/php.md) is available through Composer for PHP 8.1 and later.

**June 19, 2026**

## Scrape Word documents

* Markdown, HTML, and Crawl now accept [DOCX and legacy DOC URLs](https://docs.context.dev/scrape/pdfs-and-documents.md), returning structured document content without a separate conversion step.

**June 18, 2026**

## Page metadata

* Scrape and crawl responses now include [page metadata](https://docs.context.dev/scrape/overview) such as title, description, language, canonical URL, and structured data.
* Metadata survives content filtering, and relative resources resolve against the final URL after redirects.

**June 17, 2026**

## Hourly usage

* View [hourly calls and credit consumption](https://docs.context.dev/optimization/usage-and-logs.md) for today and yesterday in the dashboard.

## Response compression

* Use `Accept-Encoding: gzip` to reduce transfer sizes for large API responses.
* See [Compression](https://docs.context.dev/optimization/best-practices.md) for client setup and verification.

**June 16, 2026**

## Identify missing pages

* Scrape and Crawl now return `404` for missing pages, separating them from other website-access failures.
* See [Troubleshooting](https://docs.context.dev/optimization/troubleshooting.md) for status handling.

## Faster usage logs

* Large [usage histories](https://docs.context.dev/optimization/usage-and-logs.md) load and filter faster, including organizations with millions of request logs.

**June 14, 2026**

## Affiliate program

* The new [affiliate program](https://partners.dub.co/context-dev) pays 25% of referred customer payments for a year.
* See the program terms for eligibility.

**June 12, 2026**

## Export playground results

* Export a playground response as JSON, copy it, or choose **Try in Cursor** to open an implementation prompt with the response included.

**June 11, 2026**

## Context.dev CLI

* [Use Context.dev from the terminal](https://docs.context.dev/install-cli.md) with the official CLI for macOS, Linux, and Windows.
* Choose JSON or YAML output, transform responses, and pipe results into scripts or coding-agent workflows.

## Retry guidance for rate limits

* Rate-limited responses include `key_metadata` with zero credits consumed and a `Retry-After` header.
* Use the reset delay before sending another request.
* See [Rate limits](https://docs.context.dev/optimization/rate-limits.md).

## Credits used and remaining

* JSON responses to recognized API keys now include [`credits_consumed`](https://docs.context.dev/account/credits) and `credits_remaining` in `key_metadata`, including on validation errors and timeouts.
* Responses to invalid keys omit it.

## Filter logs by status

* Filter dashboard [request logs](https://docs.context.dev/optimization/usage-and-logs.md) by HTTP status to find failures and investigate integration issues.

**June 10, 2026**

## Documentation refresh

* Updated [guides](https://docs.context.dev/introduction.md) and navigation make setup and API details easier to find for developers and coding agents.

**June 9, 2026**

## Usage by API key

* View calls and credit [usage by API key](https://docs.context.dev/optimization/usage-and-logs.md) in the dashboard, with names shown where available.

**June 8, 2026**

## Filter content with CSS selectors

* Use `includeSelectors` and `excludeSelectors` to scope HTML, Markdown, and crawl content.
* Exclusion wins when both match; non-HTML documents are unaffected.
* See [Content controls](https://docs.context.dev/scrape/content-filtering.md).

**June 7, 2026**

## Read underlying XML

* [HTML scraping](https://docs.context.dev/scrape/html.md) now returns the underlying XML for styled sitemaps and feeds, rather than a browser's rendered XML viewer.
* The response identifies the detected content type.

**June 6, 2026**

## Custom request headers

* Send [custom target headers](https://docs.context.dev/scrape/location-and-headers.md#target-headers), including language preferences or authorized credentials.
* Requests with custom headers bypass the shared cache.
* Keep your Context.dev API key separate from headers sent to the target site.

**June 1, 2026**

## Backed by Y Combinator

* Context.dev is now backed by [Y Combinator](https://www.ycombinator.com/).

**May 30, 2026**

## Cache and search controls

* The [Styleguide](https://docs.context.dev/brand/styleguide.md) playground adds cache-age presets.
* Web Search also supports more Markdown, PDF, freshness, and timing controls, with updated SDK examples.

**May 25, 2026**

## Per-minute rate limits

* API limits now use a per-minute window and appear in the dashboard.
* The launch limits are 10 requests/minute for Free, 120 for Starter, 300 for Pro, and 1,200 for Scale.
* See [Rate limits](https://docs.context.dev/optimization/rate-limits.md) for current allowances.

**May 16, 2026**

## Web search

* [Search the web](https://docs.context.dev/api-reference/web-scraping/search.md) and optionally retrieve each result's Markdown in one request.
* Filter domains and freshness, expand a query, and choose content controls.

**May 14, 2026**

## SOC 2 Type I compliance

* Context.dev is now SOC 2 Type I compliant.
* Review current compliance status and evidence in the [Trust Center](https://trust.context.dev/).

## Go SDK

* The official [Go SDK](https://docs.context.dev/sdks/go.md) is available, with typed requests and responses for Context.dev APIs.

**May 11, 2026**

## Dismiss cookie banners

* Set `handleCookiePopup=true` to dismiss cookie and consent banners before [taking a screenshot](https://docs.context.dev/scrape/screenshot.md).
* The option is off by default.
* **Superseded September 22:** use `sharedParams.dismissCookies` on [Scrape](https://docs.context.dev/scrape/screenshot.md), which is on by default.

**May 10, 2026**

## PDF parsing controls

* The `pdf` object replaces `parsePDF` with controls for whether to parse a PDF and which pages to read.
* Existing requests remain compatible.
* See [PDF handling](https://docs.context.dev/parse/overview).

## Set a crawl time budget

* Give [Crawl](https://docs.context.dev/crawl/overview) a soft time budget with `stopAfterMs`.
* It checks the budget between pages and can return the pages collected so far.
* The launch default is 80 seconds, with values from 10 to 110 seconds.

**May 8, 2026**

## Wait for dynamic content

* Use `waitForMs` on supported web endpoints to allow [dynamic content](https://docs.context.dev/scrape/waiting-and-rendering.md) more time to load before capture.

**May 7, 2026**

## Screenshot dimensions and freshness

* [Screenshots](https://docs.context.dev/scrape/screenshot.md) now accept custom viewport dimensions and cache-age controls.
* Responses include the image's `width` and `height` for layout without downloading it first.

**May 6, 2026**

## Control brand-data freshness

* Control brand-data freshness with `maxAgeMs`, defaulting to three months.
* At launch, values were clamped between one day and one year.
* **Updated September 12:** values under one day, including `0` for fresh retrieval, are now honored.
* See [Cache freshness](https://docs.context.dev/optimization/best-practices.md#set-cache-freshness).

**May 5, 2026**

## Image caching and enrichment

* [Images](https://docs.context.dev/scrape/images.md) adds caching and optional dimensions, hosted copies, MIME types, and asset classification.
* Standard requests remain 1 credit; enabling any enrichment option costs 5 credits per call.
* Use `maxAgeMs=0` to request fresh results.

**May 3, 2026**

## Better wordmark detection

* [Logo extraction](https://docs.context.dev/brand/overview) better recognizes wordmarks composed of an image and adjacent brand text.

**May 1, 2026**

## Include iframe content

* Set `includeFrames=true` to include [rendered iframe content](https://docs.context.dev/scrape/content-filtering.md) in HTML, Markdown, and crawl results.
* The option is off by default.

**April 27, 2026**

## Playground controls and docs

* [Playground](https://context.dev/dashboard) endpoints now link to their documentation and expose their parameters in the UI.

**April 25, 2026**

## Explore more usage history

* Browse paginated [request history](https://docs.context.dev/optimization/usage-and-logs.md), filter every endpoint your organization has used, and view longer date ranges.
* Interactive chart legends let you toggle paths and statuses.

**April 23, 2026**

## Scrape PDF URLs

* HTML, Markdown, and Crawl now process PDF URLs, with parsing controls and skipped-page counts.
* PDF scraping launched with automatic OCR; OCR became opt-in on August 6.
* See [Parse documents](https://docs.context.dev/parse/overview) for current controls and billing.

## Crawl freshness controls

* Set `maxAgeMs` on [Crawl](https://docs.context.dev/crawl/overview) to control how long cached results can be reused.

**April 21, 2026**

## Font-file URLs

* Styleguide responses add `fontLinks`, mapping font families and weights to available file URLs.
* The result distinguishes Google Fonts and custom fonts.
* See [Extract a design system](https://docs.context.dev/brand/styleguide.md).

**April 19, 2026**

## Filter mapped URLs

* Filter mapped URLs with `urlRegex`.
* See [Map website URLs](https://docs.context.dev/map/overview) for examples.

**April 16, 2026**

## Credit charts and log search

* Track [credits over time](https://docs.context.dev/optimization/usage-and-logs.md) alongside API calls, see usage by endpoint, and search request logs by input.

**April 11, 2026**

## Multiple API keys

* Create and manage [multiple API keys](https://docs.context.dev/account/api-keys.md) from the dashboard to separate integrations and rotate credentials.

**April 7, 2026**

## More social platforms

* [Brand social links](https://docs.context.dev/brand/overview) now include WhatsApp, Telegram, and Line, bringing supported platforms to 31.

**April 5, 2026**

## Brand website language

* [Brand profiles](https://docs.context.dev/brand/overview) include `primary_language`, identifying the detected primary language of the website.

**April 4, 2026**

## Website crawling

* [Crawl a website](https://docs.context.dev/crawl/overview) from a starting URL and return collected pages as Markdown.
* Limit pages and depth, filter URLs, and choose whether to follow subdomains.
* Successful pages cost 1 credit each; the response includes per-page outcomes and totals.

**April 3, 2026**

## Styleguide update

* Styleguide extraction is faster and adds ready-to-use `css` fields.
* The `prioritize` parameter is removed; prioritization is handled automatically.
* See [Extract a design system](https://docs.context.dev/brand/styleguide.md).

**March 28, 2026**

## Keep main page content

* Set `useMainContentOnly=true` to focus [Markdown output](https://docs.context.dev/scrape/overview) on primary page content and remove navigation, sidebars, headers, and footers.

**March 25, 2026**

## Discover background images

* [Image scraping](https://docs.context.dev/scrape/images.md) now discovers CSS background images in addition to standard image elements.

## Control URL mapping

* Set `maxLinks` to control URL mapping from 1 to 100,000 links.
* At this release, the returned `urls` array remains capped at 500.
* See [Map website URLs](https://docs.context.dev/map/overview) for current limits.

**March 21, 2026**

## Brand.dev is now Context.dev

* Brand.dev is now Context.dev, reflecting the expansion from brand data into web scraping and extraction.
* Existing integrations remain compatible without code changes.
* Earlier entries use the current product name and documentation links.

**March 20, 2026**

## Better logo detection

* [Logo detection](https://docs.context.dev/brand/overview) filters more decorative icons and other shapes that are not the company's logo.

**March 17, 2026**

## Company lookup by country

* Provide `country_gl` when [looking up a company by name](https://docs.context.dev/brand/lookup-by-name.md) to distinguish companies with the same name in different countries.

**March 8, 2026**

## Credit-based pricing

* API pricing moves from calls to [credits](https://docs.context.dev/account/credits.md).
* Existing quotas convert at 10 credits per call, so 3,000 calls becomes 30,000 credits.
* Standard brand lookups remain 10 credits, while lighter scraping operations cost 1 credit.

**March 7, 2026**

## Scraping in the playground

* Try HTML, Markdown, Images, and URL mapping directly from the [dashboard playground](https://context.dev/dashboard).

**March 6, 2026**

## HTML, Markdown, Images, and URL mapping APIs

* Four new APIs turn URLs into [HTML](https://docs.context.dev/scrape/html.md), [Markdown](https://docs.context.dev/scrape/markdown.md), [images](https://docs.context.dev/scrape/images.md), or a [website URL inventory](https://docs.context.dev/map/overview).
* Scraping includes automatic proxy handling without a separate proxy charge.

**February 28, 2026**

## Verify transaction matches

* Set `high_confidence_only=true` on [transaction lookups](https://docs.context.dev/brand/lookup-by-transaction.md) to request extra verification of the merchant match.
* It defaults to `false`.

**February 23, 2026**

## Styleguides from an exact page

* [Extract a styleguide](https://docs.context.dev/brand/styleguide.md) from an exact page with `directUrl`.
* Provide either a domain or a direct URL.

**February 22, 2026**

## Lower API latency

* API requests return faster across endpoints.

**February 10, 2026**

## Larger plan quotas

* Monthly quotas increase from 2,000 to 3,000 calls on Starter and from 10,000 to 20,000 on Pro, without a price increase.
* Legacy 1,000- and 1,500-call plans move to 3,000; 15,000-call plans move to 20,000.
* Existing customer prices remain locked in, and their quotas will not be reduced. See [plans and billing](https://docs.context.dev/account/billing.md) for current allowances.

**February 1, 2026**

## Logo Link

* [Logo Link](https://docs.context.dev/brand/logo-link.md) is available: display a company's logo using a URL built from its domain.

**January 31, 2026**

## Updated guides

* Updated [setup instructions](https://docs.context.dev/quickstart.md) and task guides make it easier to find the right API and make a first request.

**January 25, 2026**

## Context.dev for Make

* [Connect Context.dev to Make](https://docs.context.dev/nocode/make.md) to build automations with other apps.

**January 15, 2026**

## More accurate social links

* [Brand retrieval](https://docs.context.dev/brand/overview) no longer returns generic social-network homepages as company profiles.

**January 14, 2026**

## Dashboard redesign

* The [developer dashboard](https://context.dev/dashboard) has a new layout and navigation for API tools and account management.

**January 3, 2026**

## More playground tools

* Email-based brand lookup and font extraction are now available in the [dashboard playground](https://context.dev/dashboard).

**January 1, 2026**

## Faster brand retrieval

* [Brand retrieval](https://docs.context.dev/brand/overview) is faster for domains that have not already been cached.

**December 22, 2025**

## Prefetch by work email

* [Prefetch brand data from a work email](https://docs.context.dev/brand/prefetching.md) before you need the result.
* The operation costs 0 credits for paid subscribers and rejects free or disposable email addresses with `422`.

**December 15, 2025**

## Fewer duplicate backdrops

* Backdrop processing removes duplicate images from [brand results](https://docs.context.dev/brand/overview).

**December 10, 2025**

## Merchant phone numbers

* Include a merchant `phone` number in [transaction enrichment](https://docs.context.dev/brand/lookup-by-transaction.md) to help verify the company match.

**November 27, 2025**

## Request brand updates

* [Request a brand-data update](https://www.context.dev/update) for incorrect logos, colors, or company details.
* The launch offers review within 24 hours.

**November 24, 2025**

## More context for transaction matching

* Improve merchant matching with an optional category code (`mcc`), city, and country (`country_gl`).
* See [Transaction enrichment](https://docs.context.dev/brand/lookup-by-transaction.md).

**November 16, 2025**

## Billing on successful requests

* At this release, billing changed to charge only successful `200` responses, leaving invalid inputs, inaccessible domains, and rejected email types unbilled.
* See [current billing guidance](https://docs.context.dev/account/credits.md#when-requests-are-charged) for today's policy.

**November 15, 2025**

## Clearer demo errors

* Demos explain invalid inputs more clearly, and website links and missing-page handling have been corrected.

**November 10, 2025**

## Sign in with GitHub

* [Sign up or sign in](https://context.dev/signup) to Context.dev with GitHub.

**October 31, 2025**

## Brand lookup by email

* [Look up a brand from a work email](https://docs.context.dev/brand/lookup-by-email.md).
* The API extracts the company domain and returns a specific error for free or disposable email providers.

**October 29, 2025**

## More brand lookup options

* Brand lookup documentation now covers domain, company-name, and ticker inputs with a consistent response shape.
* See [Get brand data](https://docs.context.dev/brand/overview).

**October 25, 2025**

## Faster API responses

* API requests return faster across endpoints.

**October 13, 2025**

## Fewer false logo matches

* [Logo detection](https://docs.context.dev/brand/overview) rejects more decorative icons that could otherwise be mistaken for company logos.

**October 8, 2025**

## International ticker exchanges

* Set `ticker_exchange` to distinguish the same ticker across international exchanges.
* Without it, the lookup assumes a US listing.
* See [Look up by ticker](https://docs.context.dev/brand/lookup-by-ticker.md).

**September 27, 2025**

## Zapier 2.0

* Zapier 2.0 adds three actions, updates brand retrieval, and includes new recipes.
* See the [Zapier guide](https://docs.context.dev/nocode/zapier.md) for the current action catalog.

**September 22, 2025**

## API History beta

* The dashboard's new [API History](https://docs.context.dev/optimization/usage-and-logs.md) beta shows request activity and consumption trends.

## Corrected usage charts

* Fixed incorrect displays in the dashboard's [request-history charts](https://docs.context.dev/optimization/usage-and-logs.md).

## Faster uncached brand lookups

* [Brand retrieval](https://docs.context.dev/brand/overview) returns results faster for uncached domains.

**September 15, 2025**

## Styleguide controls

* Styleguide adds a `prioritize` choice between speed and quality.
* Styleguide removes this parameter in April 2026; follow the current [design-system guide](https://docs.context.dev/brand/styleguide.md).

**September 7, 2025**

## Faster styleguide extraction

* [Styleguide extraction](https://docs.context.dev/brand/styleguide.md) returns results faster.

## Company website links

* [Brand profiles](https://docs.context.dev/brand/overview) add a `links` object for discovered careers, blog, terms, privacy, contact, and pricing pages.

**September 1, 2025**

## Starter pricing

* Starter pricing changes for new customers.
* Existing customers retain their previous [plan rates](https://docs.context.dev/account/billing.md).

**August 31, 2025**

## Download invoices

* View and download [invoices](https://docs.context.dev/account/billing.md) from the dashboard.

**August 27, 2025**

## One site for docs and account tools

* Account management and documentation now share the main website, removing the need to switch to a separate developer-portal domain.

**August 21, 2025**

## Change plans directly

* [Upgrade or downgrade a plan](https://docs.context.dev/account/billing.md#change-a-plan) without cancelling it first.

**August 20, 2025**

## Richer brand previews

* [Brand previews](https://docs.context.dev/brand/overview) now include contact email, phone, industries, and backdrops.

**August 19, 2025**

## Industry and subindustry labels

* Brand profiles add [Easy Industry Classification](https://docs.context.dev/classification/eic.md) in `industries.eic`, with industry and subindustry labels.

**August 18, 2025**

## Look up by name or ticker

* Look up brand profiles by company name or stock ticker, in addition to domain.
* See [Get brand data](https://docs.context.dev/brand/overview) for supported lookup methods.

**August 10, 2025**

## More wordmark coverage

* Improved [wordmark extraction](https://docs.context.dev/brand/overview) and refreshed brand records increase the coverage of wide brand logos.

**August 4, 2025**

## Keep history when rotating keys

* [Rotating an API key](https://docs.context.dev/account/api-keys.md#inspect-usage-and-retire-keys) no longer clears request history.
* Usage remains attached to the organization, including historical calls.

**July 22, 2025**

## Adult-content classification

* [Brand profiles](https://docs.context.dev/brand/overview) add `is_nsfw` to help applications identify adult-content websites.

**July 21, 2025**

## Higher-resolution logos

* [Logo extraction](https://docs.context.dev/brand/overview) prioritizes higher-resolution sources and filters low-quality variants.

**July 20, 2025**

## Original search API retired

* The original search endpoint is retired and returns `410 Gone`.
* This historical retirement does not apply to the [Web Search](https://docs.context.dev/api-reference/web-scraping/search.md) and [Brand Search](https://docs.context.dev/api-reference/brand-intelligence/search.md) APIs introduced in 2026.

**July 19, 2025**

## Company names and dashboard feedback

* Updates on July 13 and 19 improve extracted company names and add a dashboard feedback widget for reporting data issues and suggestions.

**July 10, 2025**

## Clearer API errors

* Invalid endpoints and request parameters now return [clearer errors](https://docs.context.dev/optimization/troubleshooting.md), with improved traffic protection for service availability.

**July 3, 2025**

## Typography through Styleguide

* Use [Styleguide](https://docs.context.dev/brand/styleguide.md) for detailed typography, including families, weights, sizes, line heights, and spacing.
* It provides more typography detail than the Brand response.

**July 2, 2025**

## Faster screenshots and styleguides

* [Screenshot](https://docs.context.dev/scrape/screenshot.md) and Styleguide requests are faster for both cached and newly captured pages.

**June 20, 2025**

## Screenshot API beta

* The beta [Screenshot API](https://docs.context.dev/scrape/screenshot.md) captures viewport or full-page images and returns a hosted image URL.

**June 19, 2025**

## Styleguide API beta

* The beta [Styleguide API](https://docs.context.dev/brand/styleguide.md) extracts colors, typography, spacing, shadows, and component styles for application theming.

**June 12, 2025**

## Developer portal and affiliates

* The developer portal has updated navigation and documentation.
* The original affiliate program launches with 20% commission; a new program replaces it in June 2026.
* See [current affiliate terms](https://partners.dub.co/context-dev).

**June 11, 2025**

## Faster brand retrieval

* On-demand brand retrieval returns results faster.

**June 10, 2025**

## Brand prefetching

* Paid subscribers can [prefetch brand data](https://docs.context.dev/brand/prefetching.md) before it is needed, at 0 credits, to reduce the wait for a later lookup.

**June 8, 2025**

## Speed and timeout controls

* Use `maxSpeed` for faster Brand lookups with less detail, and `timeoutMS` to set a request deadline.
* Timed-out requests return `408`. See [Timeouts](https://docs.context.dev/optimization/timeouts.md) for the current replacement syntax and limits.

**June 5, 2025**

## Request-history filters

* Filter dashboard [request history](https://docs.context.dev/optimization/usage-and-logs.md) by recent periods, longer date ranges, or all available history.

**May 30, 2025**

## First Zapier integration

* The first [Zapier integration](https://docs.context.dev/nocode/zapier.md) launches with a brand-retrieval action.

**May 29, 2025**

## Ruby SDK and image metadata

* The official [Ruby SDK](https://docs.context.dev/sdks/ruby.md) is available.
* Image metadata also adds `has_opaque_background` for assets with their own background.

**May 23, 2025**

## Python SDK

* The official [Python SDK](https://docs.context.dev/sdks/python.md) is available.

**May 20, 2025**

## Typed TypeScript SDK

* The rewritten [TypeScript SDK](https://docs.context.dev/sdks/typescript.md) exposes request and response types for easier integration.

**May 15, 2025**

## Faster brand lookups

* [Brand lookups](https://docs.context.dev/brand/overview) return results faster.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.