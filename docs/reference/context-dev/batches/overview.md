# Batches

> Scrape up to 100,000 URLs, or crawl a site, as one asynchronous job with the same outputs as Scrape Anything.

A batch scrapes many pages as one asynchronous job. Submit up to 100,000 URLs, or a crawl from a start URL or sitemap, and you get a batch ID right away. Select Scrape Anything outputs for every page, then read the results as paginated JSON or download them as files.

## What batches support

Choose a mode and one or more outputs:

| Field | Values |
| - | - |
| `input.mode` | `scrape` scrapes a list of URLs ([Submit a batch](https://docs.context.dev/batches/submit.md)). `crawl` follows links from a start URL or reads a domain's sitemap ([Large crawls](https://docs.context.dev/crawl/async.md)). |
| `input.data.formats` | Any combination of `markdown`, `html`, `screenshot`, `images`, `bytes`, `parse`, `product`, `highlights`, and `json`. |

Batches use the same parameters and per-page result schema as [Scrape Anything](https://docs.context.dev/scrape/overview). See [Submit a batch](https://docs.context.dev/batches/submit.md) for extraction options, page deadlines, and pricing. Add `policies` to apply [access policies](https://docs.context.dev/optimization/access-policies.md) to every page.

## Submit a URL list

This request scrapes two pages as Markdown and HTML. The examples read your API key from `CONTEXT_DEV_API_KEY`; the [Quickstart](https://docs.context.dev/quickstart.md) shows how to create a key and install an SDK.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({ apiKey: process.env.CONTEXT_DEV_API_KEY });

const batch = await client.batch.submit({
  input: {
    mode: "scrape",
    data: {
      formats: { markdown: true, html: true },
      urls: [
        { url: "https://example.com/about", itemId: "about" },
        { url: "https://example.com/careers", itemId: "careers" },
      ],
    },
  },
  "Idempotency-Key": "site-import-2026-09-26",
});
console.log(batch.id, batch.status);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

batch = client.batch.submit(
    input={
        "mode": "scrape",
        "data": {
            "formats": {"markdown": True, "html": True},
            "urls": [
                {"url": "https://example.com/about", "item_id": "about"},
                {"url": "https://example.com/careers", "item_id": "careers"},
            ],
        },
    },
    idempotency_key="site-import-2026-09-26",
)
print(batch.id, batch.status)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

batch = client.batch.submit(
  input: {
    mode: "scrape",
    data: {
      formats: {markdown: true, html: true},
      urls: [
        {url: "https://example.com/about", item_id: "about"},
        {url: "https://example.com/careers", item_id: "careers"},
      ],
    },
  },
  idempotency_key: "site-import-2026-09-26",
)
puts batch.id, batch.status
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
	body := map[string]any{"input": map[string]any{"mode": "scrape", "data": map[string]any{
		"formats": map[string]bool{"markdown": true, "html": true},
		"urls": []map[string]any{{"url": "https://example.com/about", "itemId": "about"}, {"url": "https://example.com/careers", "itemId": "careers"}},
	}}}
	var response map[string]any
	err := client.Post(context.Background(), "/batch/submit", body, &response, option.WithHeader("Idempotency-Key", "site-import-unified-v1"))
	if err != nil { panic(err) }
	fmt.Println(response["id"], response["status"])
}
```

```php PHP theme={null}
<?php
require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$batch = $client->batch->submit(
    input: [
        "mode" => "scrape",
        "data" => [
            "formats" => ["markdown" => true, "html" => true],
            "urls" => [
                ["url" => "https://example.com/about", "itemID" => "about"],
                ["url" => "https://example.com/careers", "itemID" => "careers"],
            ],
        ],
    ],
    idempotencyKey: "site-import-2026-09-26",
);
echo $batch->id, " ", $batch->status, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/batch/submit \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: site-import-2026-09-26" \
  -d '{
    "input": {
      "mode": "scrape",
      "data": {
        "formats": { "markdown": true, "html": true },
        "urls": [
          { "url": "https://example.com/about", "itemId": "about" },
          { "url": "https://example.com/careers", "itemId": "careers" }
        ]
      }
    }
  }'
```

The API returns `202` with the new batch (trimmed):

```json theme={null}
{
  "id": "batch_9f2c8a",
  "status": "queued",
  "mode": "scrape",
  "tags": [],
  "crawl": null,
  "formats": { "markdown": true, "html": true },
  "input": {
    "reserved": 2,
    "reserved_is_ceiling": false,
    "submitted": 2,
    "duplicates": 0,
    "invalid": 0
  },
  "credits": { "reserved": 2 },
  "invalid_urls": [],
  "created_at": "2026-09-26T12:00:00.000Z"
}
```

Save `id`. `input.submitted` counts the URLs you sent. `input.reserved` counts the pages the batch will attempt once duplicates and invalid URLs are removed, and `credits.reserved` is what was held for them. `invalid_urls` lists up to 100 rejected URLs, each with a `reason` such as `Must be a public http:// or https:// URL`. A submission with a `webhook` also returns `webhook_secret`, which only this response includes. The `Idempotency-Key` header makes a retried submit return this batch instead of creating a second one; see [Idempotency](https://docs.context.dev/batches/submit.md#idempotency).

## Lifecycle

| Status | Meaning |
| - | - |
| `queued` | Accepted and waiting to start. |
| `running` | Pages are being scraped. |
| `cancelling` | A cancel was requested. Pages already in progress finish first. |
| `completed` | Every accepted page was attempted. Individual pages can still have failed. |
| `cancelled` | Stopped by a cancel request. |
| `failed` | The batch itself stopped. `failure.code` says why. |

`completed`, `cancelled`, and `failed` are final. Poll the batch or add a [webhook](https://docs.context.dev/webhooks.md) to find out when it reaches one, then read the results. See [Status and results](https://docs.context.dev/batches/results.md).

## Access

A restricted API key needs `batches:write` to submit, cancel, or delete batches and to replay their webhook deliveries. `batches:read` covers status, results, the batch list, and delivery history. See [API keys](https://docs.context.dev/account/api-keys.md).

## Choose an endpoint

| You need | Use |
| - | - |
| One page, or an output or option that batches don't support | [Scrape](https://docs.context.dev/scrape/overview) |
| Up to 500 linked pages returned in one response | [Crawl](https://docs.context.dev/crawl/overview) |
| Up to 100,000 known URLs, or a crawl of more than 500 pages | A batch |
| A list of a site's URLs to put in a batch | [Map URLs](https://docs.context.dev/map/overview) |

## Related

* [Submit a batch](https://docs.context.dev/batches/submit.md): URL lists, page options, deduplication, and idempotency.
* [Status and results](https://docs.context.dev/batches/results.md): progress, result records, files, and how long results are kept.
* [Cancel, limits, and errors](https://docs.context.dev/batches/limits-and-errors.md): cancel and delete, concurrency, and error codes.
* [Webhooks](https://docs.context.dev/webhooks.md): signatures, retries, and replay for `batch.*` events.
* [Submit a batch reference](https://docs.context.dev/api-reference/batches/submit.md)


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.