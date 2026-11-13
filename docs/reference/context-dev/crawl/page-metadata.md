# Page metadata

> Read the per-page metadata, run counters, and cache status in a crawl response.

A `POST /web/crawl` response carries metadata at two levels. Each item in `results` has a `metadata` object describing that page, and the response itself has a run-level `metadata` object with counters for the whole crawl, plus `cache_metadata`.

## Read a crawl response

Send this body to `POST /web/crawl`. See the [Quickstart](https://docs.context.dev/quickstart.md) for authentication and SDK setup.

```json theme={null}
{
  "url": "https://docs.context.dev/introduction",
  "maxPages": 3,
  "maxDepth": 1
}
```

Abridged response:

```json theme={null}
{
  "results": [
    {
      "markdown": "# Introduction\n\nContext gives agents live web data.",
      "metadata": {
        "url": "https://docs.context.dev/introduction",
        "sourceUrl": "https://docs.context.dev/introduction",
        "finalUrl": "https://docs.context.dev/introduction",
        "title": "Introduction",
        "crawlDepth": 0,
        "statusCode": 200,
        "success": true,
        "description": "Live web data for agents.",
        "language": "en",
        "headings": [{"level": 1, "text": "Introduction"}]
      }
    }
  ],
  "metadata": {
    "numUrls": 3,
    "maxCrawlDepth": 1,
    "numSucceeded": 3,
    "numFailed": 0,
    "numSkipped": 0
  },
  "cache_metadata": {"status": "miss", "age_ms": 0},
  "request_id": "d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37"
}
```

## Per-page metadata

`results[].metadata` always has these crawl-specific fields:

| Field | Notes |
| - | - |
| `url` | String. The crawl URL fetched for this page. |
| `sourceUrl` | String. Original URL requested by the caller. |
| `finalUrl` | String. Final URL scraped after redirects or scraper fallback, when known. Falls back to `sourceUrl` when unavailable. |
| `title` | String. Best page title extracted from the page; an empty string if unavailable. |
| `crawlDepth` | Integer. Depth relative to the start URL: `0` is the start URL, `1` is one link away. |
| `statusCode` | Integer. HTTP status code of the response. |
| `success` | Boolean. `true` if the page was fetched and parsed successfully. |

The same object also carries the fields Scrape extracts from page HTML: `description`, `language`, `keywords`, `canonicalUrl`, `author`, `siteName`, `image`, `favicon`, `publishedTime`, `modifiedTime`, `robots`, `openGraph`, `twitter`, `alternates`, `headings`, `jsonLd`, and `additionalMeta`. They are omitted when not found. See [Scrape page metadata](https://docs.context.dev/scrape/page-metadata.md) for each field.

A failed page keeps its `metadata` entry with `success: false` and an empty `markdown` string, so check `success` before using the content.

## Run metadata

The top-level `metadata` object summarizes the run. Every counter is always present.

| Field | Notes |
| - | - |
| `numUrls` | Integer. Total number of URLs crawled. |
| `maxCrawlDepth` | Integer. Maximum crawl depth reached during the crawl. |
| `numSucceeded` | Integer. Number of pages successfully crawled. |
| `numFailed` | Integer. Number of pages that failed to crawl. |
| `numSkipped` | Integer. Number of URLs skipped: PDFs when `pdf.shouldParse` is `false`, URLs not matching `urlRegex`, or URLs matching `excludeUrlRegex`. |

Read `partial` alongside these counters. It is `true` when `timeoutOpts.behavior` is `return-partial` and the crawl returned the usable results collected before the deadline; partial collections are not cached as complete results.

## Cache metadata

| Field | Notes |
| - | - |
| `cache_metadata.status` | `hit`, `miss`, or `zdr`: whether the response was served from cache, required fresh work, or honored a zero-data-retention cache bypass. |
| `cache_metadata.age_ms` | Integer. Age of the cached data in milliseconds; `0` for `miss` and `zdr` responses. |

Set `maxAgeMs` to control how old cached page content may be; see [page content](https://docs.context.dev/crawl/page-content.md).

## Related

* [Crawl overview](https://docs.context.dev/crawl/overview): the request and how to iterate `results`.
* [Scrape page metadata](https://docs.context.dev/scrape/page-metadata.md): descriptions of the shared per-page fields.
* [Scope and limits](https://docs.context.dev/crawl/scope.md): the filters that decide which URLs are crawled or skipped.
* [Freshness and caching](https://docs.context.dev/scrape/freshness-and-caching.md): how cached outputs are reused.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.