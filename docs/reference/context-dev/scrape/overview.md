# Scrape

> Get page content, images, structured data, and screenshots from one URL.

Scrape visits a URL and returns the outputs you enable in `formats`. Combine formats in one request and check each output’s `success` before using its data.

## Make a request

Set up your API key and SDK in the [Quickstart](https://docs.context.dev/quickstart.md). This request returns the page’s main content as Markdown.

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const page = await client.web.scrape({
  url: "https://example.com",
  formats: { markdown: true },
  sharedParams: { mainContentOnly: true },
});

console.log(page.metadata.title);
console.log(page.markdown.data);
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

page = client.web.scrape(
    url="https://example.com",
    formats={"markdown": True},
    shared_params={"main_content_only": True},
)

print(page.metadata.title)
print(page.markdown.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {markdown: true},
  shared_params: {main_content_only: true},
)

puts page.metadata.title
puts page.markdown.data
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
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    page, err := client.Web.Scrape(context.Background(), contextdev.WebScrapeParams{
        URL:          "https://example.com",
        Formats:      contextdev.WebScrapeParamsFormats{Markdown: contextdev.Bool(true)},
        SharedParams: contextdev.WebScrapeParamsSharedParams{MainContentOnly: contextdev.Bool(true)},
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(page.Metadata.Title)
    fmt.Println(page.Markdown.Data)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['markdown' => true],
    url: 'https://example.com',
    sharedParams: ['mainContentOnly' => true],
);

echo $page->metadata->title, PHP_EOL;
echo $page->markdown->data, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": { "markdown": true },
    "sharedParams": { "mainContentOnly": true }
  }'
```

## Read the response

Every output has `requested`, `success`, and `data`. A successful output has `success: true`. Failed outputs have `success: false`, `data: null`, and an `error_code` and `message`; outputs you did not request have `success: null`. One failed output can coexist with successful ones in an HTTP 200 response.

Abridged response:

```json theme={null}
{
  "url": "https://example.com/",
  "markdown": {"requested": true, "success": true, "data": "# Example Domain"},
  "metadata": {"title": "Example Domain"},
  "cache_metadata": {"status": "miss", "age_ms": 0},
  "request_id": "d7aa1c3a-38d2-4fb5-92c8-0f0cac3efa37"
}
```

`profile` contains the browser profile ID or `null`; see [browser profiles](https://docs.context.dev/scrape/browser-profiles.md). `isPartial` flags incomplete results. Every response includes `metadata`, which describes the page regardless of the formats you request; see [page metadata](https://docs.context.dev/scrape/page-metadata.md). `key_metadata` reports request usage. Save `request_id` when investigating failures.

## Formats

| Format | Output | Guide |
| - | - | - |
| `html` | Rendered HTML | [HTML](https://docs.context.dev/scrape/html.md) |
| `markdown` | Text with Markdown formatting | [Markdown](https://docs.context.dev/scrape/markdown.md) |
| `screenshot` | Inline image data URL | [Screenshot](https://docs.context.dev/scrape/screenshot.md) |
| `images` | Image URLs and optional enrichment | [Images](https://docs.context.dev/scrape/images.md) |
| `bytes` | Original response bytes as base64 | [Bytes](https://docs.context.dev/scrape/bytes.md) |
| `parse` | Structured data in `parsed.data` | [Custom parser](https://docs.context.dev/scrape/parse-fields.md), [Pre-built parsers](https://docs.context.dev/scrape/prebuilt-parsers) |
| `highlights` | Passages relevant to a question | [Highlights](https://docs.context.dev/scrape/highlights.md) |
| `json` | An object matching your JSON Schema | [JSON](https://docs.context.dev/scrape/json.md) |
| `product` | Product details and availability | [Product](https://docs.context.dev/scrape/product.md) |

Parsing defaults to custom CSS rules. Set `parseParams.type` to `"prebuilt"` to select a supported parser. The `parsed.type` response field is `"custom"` or the selected parser name.

## Shape the page visit

Use `sharedParams` for [browser profiles](https://docs.context.dev/scrape/browser-profiles.md), [browser actions](https://docs.context.dev/scrape/browser-actions.md), [waiting and rendering](https://docs.context.dev/scrape/waiting-and-rendering.md), [content filtering](https://docs.context.dev/scrape/content-filtering.md), [location and headers](https://docs.context.dev/scrape/location-and-headers.md), or [PDF parsing](https://docs.context.dev/scrape/pdfs-and-documents.md).

Use `maxAgeMs` for [freshness](https://docs.context.dev/scrape/freshness-and-caching.md), `timeoutOpts` for [deadlines](https://docs.context.dev/scrape/timeouts-and-errors.md), `zdr` for [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md), `policies` for [access policies](https://docs.context.dev/optimization/access-policies.md) a URL must pass, and `tags` for [usage tracking](https://docs.context.dev/optimization/usage-and-logs.md). The [reference](https://docs.context.dev/api-reference/web-scraping/scrape.md) lists the complete request and response.

## Choose another API

Use [Map](https://docs.context.dev/map/overview) to find a site’s URLs, [Crawl](https://docs.context.dev/crawl/overview) to read several pages, or [Batches](https://docs.context.dev/batches/overview) to process a URL list asynchronously. [Search](https://docs.context.dev/search/overview) finds pages from a query; [Answers](https://docs.context.dev/answers/overview) researches a question. [Parse](https://docs.context.dev/parse/overview) accepts uploaded files.

## Move from the per-format endpoints

The older routes remain available. New integrations can request several formats through `POST /web/scrape`:

| Earlier route | Request on Scrape | Read |
| - | - | - |
| `GET /web/scrape/html` | `formats.html: true` | `html.data` |
| `GET /web/scrape/markdown` | `formats.markdown: true` | `markdown.data` |
| `GET /web/scrape/screenshot` | `formats.screenshot: true` | `screenshot.data` |
| `GET /web/scrape/images` | `formats.images: true` | `images.data` |
| `GET /web/scrape/bytes` | `formats.bytes: true` | `bytes.data` |
| `GET /web/scrape/sitemap` | Use [Map URLs](https://docs.context.dev/map/overview) | `urls` |

The option names and response shapes differ. Use the format guides when migrating.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.