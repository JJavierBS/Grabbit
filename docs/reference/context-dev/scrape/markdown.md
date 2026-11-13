# Markdown

> Convert page content into Markdown for search, reading, or model context.

Enable `formats.markdown` and read `markdown.data`. Headings, lists, tables, and code retain Markdown formatting. [YouTube URLs](https://docs.context.dev/scrape/youtube.md) return a video or channel document.

## Request Markdown

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

Abridged response:

```json theme={null}
{"markdown": {"requested": true, "success": true, "data": "# Example Domain\n\nThis domain is for use in examples."}}
```

## Options

| `markdownParams` field | Default | Effect |
| - | - | - |
| `includeLinks` | `true` | Keep link destinations. |
| `includeImages` | `false` | Keep image references. |
| `inlineImages` | `placeholder` | Use `preserve` to retain base64 images; requires `includeImages`. |
| `sourcePreference` | `["html-conversion", "markdown-direct"]` | Where the Markdown comes from, in order; see [Choose the Markdown source](#choose-the-markdown-source). |

## Choose the Markdown source

Many docs sites, including GitHub Docs, Mintlify, and GitBook, publish a Markdown version of each page. It often leads to a cleaner markdown than an HTML conversion, but some sites leave content out of it, such as extra code tabs.

`markdownParams.sourcePreference` lists the sources to try, in order. The first usable one wins.

| Source | Markdown |
| - | - |
| `html-conversion` | Converted from the page HTML. |
| `markdown-direct` | The Markdown the page publishes, as the site serves it. |

```json theme={null}
{
  "url": "https://docs.github.com/en/rest/quickstart",
  "formats": {
    "markdown": true
  },
  "markdownParams": {
    "sourcePreference": ["markdown-direct", "html-conversion"]
  }
}
```

* The default, `["html-conversion", "markdown-direct"]`, converts the HTML and falls back to published Markdown only for near-empty conversions.
* `["markdown-direct", "html-conversion"]` prefers published Markdown and converts the HTML when there is none.
* `["markdown-direct"]` fails with `NO_PUBLISHED_MARKDOWN` when the page publishes no Markdown. Failed requests are not billed.
* `["html-conversion"]` never uses published Markdown.

`includeLinks`, `includeImages`, and `inlineImages` only apply to `html-conversion`; requests that set them without listing `html-conversion` are rejected. Requests with `sharedParams.includeSelectors` or `sharedParams.excludeSelectors` never use `markdown-direct`, so they must include `html-conversion`. [Crawl](https://docs.context.dev/crawl/page-content.md) and [batches](https://docs.context.dev/batches/submit.md) accept the same `sourcePreference`.

## Prepare text for embeddings

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "markdown": true
  },
  "sharedParams": {
    "mainContentOnly": true
  },
  "markdownParams": {
    "includeLinks": false
  }
}
```

To keep illustrations, set `markdownParams.includeImages` to `true`. To capture matching text and a screenshot, request both formats and set `maxAgeMs: 0`.

An empty string can mean [content filters](https://docs.context.dev/scrape/content-filtering.md) matched nothing. Check the selected content before retrying. See [limits and errors](https://docs.context.dev/scrape/timeouts-and-errors.md) for failed outputs.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.