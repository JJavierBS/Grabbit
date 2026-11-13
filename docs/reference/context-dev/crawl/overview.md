# Crawl

> Read a website’s pages as Markdown in one response.

Crawl follows links from a start URL and returns Markdown for up to 500 pages. Bound the work with page, depth, path, and time limits.

## Crawl a site

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const crawl = await client.web.webCrawlMd({
  url: "https://docs.context.dev/introduction",
  maxPages: 3,
  maxDepth: 1,
  useMainContentOnly: true,
});

for (const page of crawl.results) {
  console.log(page.metadata.url, page.metadata.success);
}
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

crawl = client.web.web_crawl_md(
    url="https://docs.context.dev/introduction",
    max_pages=3,
    max_depth=1,
    use_main_content_only=True,
)

for page in crawl.results:
    print(page.metadata.url, page.metadata.success)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

crawl = client.web.web_crawl_md(
  url: "https://docs.context.dev/introduction",
  max_pages: 3,
  max_depth: 1,
  use_main_content_only: true,
)

crawl.results.each do |page|
  puts "#{page.metadata.url}: #{page.metadata.success}"
end
```

```go Go theme={null}
package main

import (
    "context"
    "fmt"
    "os"

    contextdev "github.com/context-dot-dev/context-go-sdk/v2"
    "github.com/context-dot-dev/context-go-sdk/v2/option"
    "github.com/context-dot-dev/context-go-sdk/v2/packages/param"
)

func main() {
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    crawl, err := client.Web.WebCrawlMd(context.Background(), contextdev.WebWebCrawlMdParams{
        URL: "https://docs.context.dev/introduction",
        MaxPages: param.NewOpt[int64](3),
        MaxDepth: param.NewOpt[int64](1),
        UseMainContentOnly: param.NewOpt(true),
    })
    if err != nil {
        panic(err)
    }

    for _, page := range crawl.Results {
        fmt.Println(page.Metadata.URL, page.Metadata.Success)
    }
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$crawl = $client->web->webCrawlMd(
    url: 'https://docs.context.dev/introduction',
    maxPages: 3,
    maxDepth: 1,
    useMainContentOnly: true,
);

foreach ($crawl->results as $page) {
    echo $page->metadata->url, ': ',
        $page->metadata->success ? 'success' : 'failed', PHP_EOL;
}
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/crawl \
  --request POST \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "url": "https://docs.context.dev/introduction",
    "maxPages": 3,
    "maxDepth": 1,
    "useMainContentOnly": true
  }'
```

Read each item in `results` for its URL, Markdown, and [page metadata](https://docs.context.dev/crawl/page-metadata.md); the run-level `metadata` counters and `cache_metadata` are described on the same page. The [reference](https://docs.context.dev/api-reference/web-scraping/crawl.md) lists the full response. Check `partial` when a deadline may have ended the crawl early.

## Choose the workflow

| Task | API |
| - | - |
| Read a small site in one request | Crawl |
| Process a larger site in the background | [Large crawls](https://docs.context.dev/crawl/async.md) |
| Inspect URLs before choosing pages | [Map](https://docs.context.dev/map/overview), then [Batches](https://docs.context.dev/batches/overview) |
| Interact with pages or request other outputs | [Scrape](https://docs.context.dev/scrape/overview) |

## Freshness and waits

| Field | Default | Maximum |
| - | - | - |
| `maxAgeMs` | One day (`86400000` ms) | 30 days (`2592000000` ms) |
| `waitForMs` | 3,500 ms | 30,000 ms |

`maxAgeMs` is the oldest cached page content the crawl accepts; `0` fetches fresh. `waitForMs` is the browser wait after initial page load for each crawled page. Requests also accept `policies` for [access policies](https://docs.context.dev/optimization/access-policies.md) every URL must pass and `tags` for [usage tracking](https://docs.context.dev/optimization/usage-and-logs.md).

## Scope and failures

See [scope and limits](https://docs.context.dev/crawl/scope.md) to restrict discovery and [page content](https://docs.context.dev/crawl/page-content.md) to control extraction. A missing start page returns `404 NOT_FOUND`; unsupported start-page content returns `415 UNSUPPORTED_CONTENT`.

Crawl uses one concurrency slot like other calls; on per-minute plans it has a weight of 10 in the API key’s [rate-limit bucket](https://docs.context.dev/optimization/rate-limits.md). For a job that should continue beyond a single request, use a batch.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.