# HTML

> Return the page DOM after rendering and content filtering.

Enable `formats.html` to read the rendered page in `html.data`. JavaScript, browser actions, and content filters affect this output. Use [Bytes](https://docs.context.dev/scrape/bytes.md) to inspect the original HTTP response.

## Request HTML

```typescript TypeScript theme={null}
const page = await client.web.scrape({
  url: "https://example.com",
  formats: { markdown: true, html: true },
});

console.log(page.html.data);
console.log(page.markdown.data);
```

```python Python theme={null}
page = client.web.scrape(
    url="https://example.com",
    formats={"markdown": True, "html": True},
)

print(page.html.data)
print(page.markdown.data)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

page = client.web.scrape(
  url: "https://example.com",
  formats: {markdown: true, html: true},
)

puts page.html.data
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
        URL: "https://example.com",
        Formats: contextdev.WebScrapeParamsFormats{
            Markdown: contextdev.Bool(true),
            HTML:     contextdev.Bool(true),
        },
    })
    if err != nil {
        panic(err)
    }

    fmt.Println(page.HTML.Data)
    fmt.Println(page.Markdown.Data)
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$page = $client->web->scrape(
    formats: ['markdown' => true, 'html' => true],
    url: 'https://example.com',
);

echo $page->html->data, PHP_EOL;
echo $page->markdown->data, PHP_EOL;
```

```bash cURL theme={null}
curl https://api.context.dev/v1/web/scrape \
  -H "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "formats": { "markdown": true, "html": true }
  }'
```

Abridged response:

```json theme={null}
{"html": {"requested": true, "success": true, "data": "<main><h1>Example Domain</h1></main>"}}
```

## Combine HTML with other formats

Get readable text and inspect the same visit’s DOM:

```json theme={null}
{
  "url": "https://example.com",
  "formats": {
    "html": true,
    "markdown": true
  },
  "maxAgeMs": 0
}
```

For a dynamically loaded page, add `sharedParams.waitFor` with a CSS selector such as `#results`. See [waiting and rendering](https://docs.context.dev/scrape/waiting-and-rendering.md).

## Filter and handle results

[Content filtering](https://docs.context.dev/scrape/content-filtering.md) applies before the HTML is returned. A filter that matches nothing can return an empty string with `success: true`. An output that exceeds the [response limits](https://docs.context.dev/scrape/timeouts-and-errors.md#size-limits) fails while other outputs remain available.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.