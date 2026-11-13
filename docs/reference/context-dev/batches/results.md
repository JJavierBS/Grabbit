# Status and results

> Poll a batch until it finishes, read its records as paginated JSON or gzipped NDJSON files within 180 days, and find earlier batches.

A batch is done when its status is `completed`, `cancelled`, or `failed`. Then you can page through its records as JSON or download them as files. Result files are deleted 180 days after the batch finishes.

## Check status

`GET /v1/batch/{batch_id}` returns the batch. Poll every 10 to 30 seconds while `status` is `queued`, `running`, or `cancelling`, or let a [webhook](https://docs.context.dev/webhooks.md) tell you when it's done. A finished batch (trimmed):

```json theme={null}
{
  "id": "batch_9f2c8a",
  "status": "completed",
  "mode": "scrape",
  "tags": ["site-import"],
  "crawl": null,
  "formats": { "markdown": true, "html": true },
  "input": { "reserved": 2000, "reserved_is_ceiling": false, "submitted": 2003, "duplicates": 2, "invalid": 1 },
  "progress": { "succeeded": 1998, "failed": 2, "pending": 0 },
  "credits": { "reserved": 2000, "refunded": 2, "ocr_charged": 0, "net": 1998 },
  "page_errors": [{ "code": "NOT_FOUND", "count": 2 }],
  "failure": null,
  "timing": {
    "created_at": "2026-09-26T12:00:00.000Z",
    "started_at": "2026-09-26T12:00:02.000Z",
    "completed_at": "2026-09-26T12:09:41.000Z"
  },
  "results": {
    "expires_at": "2026-09-27T12:10:05.000Z",
    "files": [{ "url": "https://storage.googleapis.com/…", "items": 50, "bytes": 184320 }]
  },
  "policies": [],
  "invalid_urls": [{ "url": "ftp://example.com/archive", "reason": "Must be a public http:// or https:// URL" }],
  "webhook_delivery_id": "whd_0f3a9c7e2b1d4e8fa6c5b4d3e2f1a0b9"
}
```

| Field | Meaning |
| - | - |
| `mode`, `tags`, `formats`, `policies` | What you submitted: `scrape` or `crawl`, the batch's tags, the requested outputs, and the [access policy](https://docs.context.dev/optimization/access-policies.md) IDs applied to every page. |
| `crawl` | How a crawl was configured; see [Crawl settings](#crawl-settings). `null` for scrape batches. |
| `input` | What the submission accepted: `reserved` pages, whether `reserved_is_ceiling` (a crawl ceiling rather than an exact count), `submitted` URLs before validation, `duplicates` dropped, and `invalid` URLs rejected. `submitted` and `invalid` are `null` for a crawl. |
| `progress.succeeded`, `progress.failed` | Pages attempted so far, by outcome. |
| `progress.pending` | Accepted pages not attempted yet. It's `0` once a batch is `completed`. A cancelled or failed batch keeps the pages it never reached here, and they have no result records. |
| `credits` | Settlement: `reserved` when the batch was accepted, `refunded` for unsuccessful pages when it settles, `ocr_charged` for OCR usage, and `net`, which is `reserved` minus `refunded` plus `ocr_charged`. |
| `page_errors` | Failed pages grouped by `error_code`, largest group first. |
| `failure` | Why the batch itself stopped: `enqueue_failed` (its work couldn't be queued) or `stalled` (no progress for an hour, even after two automatic requeues). `null` otherwise. |
| `results` | Download links. `null` until the batch is final. |
| `invalid_urls` | The first 100 rejected URLs, each with its `url` and a `reason`. |
| `webhook_delivery_id` | The delivery ID of the batch's `batch.*` event, when available. Pass it to the [delivery endpoints](https://docs.context.dev/webhooks.md#delivery-history-and-replay). |

A `batch.*` webhook carries this same object in `data.batch`, and [List batches](#list-batches) returns it too, both without `invalid_urls` and `webhook_delivery_id`.

A crawl can finish below its `maxUrls` when it runs out of pages in scope.

### Crawl settings

`crawl` records a crawl batch's settings as submitted:

| Field | Meaning |
| - | - |
| `source` | Where the crawl started: `type: "start_url"` with the `url`, or `type: "sitemap"` with the `domain` whose sitemap supplied the pages. |
| `max_pages` | The `maxUrls` submitted. A sitemap crawl scrapes only the URLs its sitemap lists, up to this many, so `input.reserved` is often lower. |
| `max_depth` | Link depth limit. Always `0` for a sitemap crawl; `null` when a `start_url` crawl set no limit. |
| `follow_subdomains` | Whether links to subdomains were followed. Always `false` for a sitemap crawl. |
| `url_pattern`, `exclude_url_pattern` | Regex patterns URLs had to match, or must not match, to be crawled. `null` when not set. |
| `languages` | `same_as_start_url`, a list of language codes whose pages were followed, or `null` when all languages were. |

## Read results

`GET /v1/batch/{batch_id}/results` pages through a finished batch's records as JSON. It returns `409 BATCH_NOT_COMPLETED` until the batch is final.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const page = await client.batch.getResults("batch_9f2c8a", { limit: 100 });
console.log(page.data.length, page.has_more, page.next_cursor);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.batch.get_results("batch_9f2c8a", limit=100)
print(len(page.data), page.has_more, page.next_cursor)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.batch.get_results("batch_9f2c8a", limit: 100)
puts page.data.length, page.has_more, page.next_cursor.inspect
```

```go Go theme={null}
package main

import (
	"context"
	"fmt"
	"os"

	contextdev "github.com/context-dot-dev/context-go-sdk/v2"
	"github.com/context-dot-dev/context-go-sdk/v2/option"
)

func main() {
	client := contextdev.NewClient(option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")))

	page, err := client.Batch.GetResults(context.Background(), "batch_9f2c8a", contextdev.BatchGetResultsParams{
		Limit: contextdev.Int(100),
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(len(page.Data), page.HasMore, page.NextCursor)
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->batch->getResults("batch_9f2c8a", limit: 100);
echo count($page->data), PHP_EOL;
var_dump($page->hasMore, $page->nextCursor);
```

```bash cURL theme={null}
curl -G https://api.context.dev/v1/batch/batch_9f2c8a/results \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --data-urlencode "limit=100"
```

```json theme={null}
{
  "data": [
    {
      "url": "https://example.com/about",
      "itemId": "about",
      "status": "ok",
      "credits_used": 1,
      "result": {
        "url": "https://example.com/about",
        "markdown": { "requested": true, "success": true, "data": "# About us\n\n…" },
        "html": { "requested": true, "success": true, "data": "<main><h1>About us</h1></main>" },
        "metadata": { "title": "About us" },
        "cache_metadata": { "status": "miss", "age_ms": 0 },
        "request_id": "4e7b5b93-0e10-42f8-949e-46c817fe43de"
      }
    },
    {
      "url": "https://example.com/careers",
      "itemId": "careers",
      "status": "error",
      "error_code": "NOT_FOUND",
      "message": "Page returned 404",
      "credits_used": 1
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

The example is abbreviated. The full `result` includes a status for every output, including those you did not request.

* `limit` is 1–100 and defaults to 25. A page can close early to stay under about 8 MB, so keep requesting with `cursor` set to `next_cursor` while `has_more` is `true`. An unknown cursor returns `400`.
* Records aren't in submission order. Match them with `itemId`; `meta` comes back too.
* A successful record has `status: "ok"`, `credits_used`, and `result`, using the same response schema as Scrape Anything. Check `result.isPartial` and each output's `success` for partial results. `ocr_pages` appears when OCR recovered PDF pages.
* A failed record has `status: "error"`, `error_code`, and `message`:

| `error_code` | Meaning |
| - | - |
| `NOT_FOUND` | The page returned 404. |
| `WEBSITE_BLOCKED` | The site served a bot challenge or an access wall. |
| `WEBSITE_ACCESS_ERROR` | No content could be fetched, or a crawl redirect left the crawl's scope. |
| `ACCESS_POLICY_DENIED` | The page redirected to a website an [access policy](https://docs.context.dev/optimization/access-policies.md) blocks. |
| `REQUEST_TIMEOUT` | The page didn't finish within its per-page deadline. Timed-out pages get one automatic retry. |
| `UNSUPPORTED_CONTENT` | The content type can't be scraped. |
| `PDF_IMAGES_ONLY` | A scanned PDF with no text layer. Set `sharedParams.parsers.pdf.ocr: "auto"` to recover text. |
| `INTERNAL_ERROR` | Context.dev couldn't process the page. |

## Download files

For large batches, download the files in `results.files` instead of paging. Each file is gzipped NDJSON, one record per line, with up to 50 records, so a 100,000-URL batch has about 2,000 files. File order carries no meaning.

Each link expires 24 hours after the call that returned it (`results.expires_at`). Retrieve the batch again for new links. The `data.batch.results` links in a `batch.*` webhook expire 24 hours after the event, and a replay resends those same links.

Result files are deleted 180 days after the batch finishes. After that, the links stop working and `/results` can't return the records, so copy what you need within 180 days.

## List batches

`GET /v1/batch/list?shouldIncludeUnified=true` returns your batches, newest first, as the same [batch object](#check-status) without `invalid_urls` and `webhook_delivery_id`. It returns 25 per page by default and up to 100 with `limit`. Filter with these parameters:

| Parameter | Notes |
| - | - |
| `shouldIncludeUnified` | Defaults to `false`, which leaves out batches submitted with `formats`. Set it to `true` to list them. |
| `status` | One status, such as `completed`. |
| `q` | Up to 200 characters. Searches batch IDs, crawl sources, and tags. |
| `search_type` | `prefix` (default) or `exact`. |
| `tags` | Comma-separated (`tags=docs,competitor`) or repeated (`tags=docs&tags=competitor`). Matches batches with any of the tags. |

Page with `cursor` set to `next_cursor`. A search with `q` or `tags` can return `503 SEARCH_UNAVAILABLE`; retry it, or list without them.

## Related

* [Submit a batch](https://docs.context.dev/batches/submit.md): `itemId`, `meta`, and page options.
* [Cancel, limits, and errors](https://docs.context.dev/batches/limits-and-errors.md): delete old batches and handle errors.
* [List batch results reference](https://docs.context.dev/api-reference/batches/results.md) and [Retrieve a batch reference](https://docs.context.dev/api-reference/batches/retrieve.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.