# Map URLs

> Discover a site’s URLs and available page metadata.

Use Map to discover a site’s URLs before choosing which pages to read. Results can include a title, description, keywords, and language. Map returns an inventory, not page content or a guarantee of complete site coverage. A site without a sitemap returns the links on its homepage; use [Crawl](https://docs.context.dev/crawl/overview) to follow links deeper.

## Map a domain

```typescript TypeScript theme={null}
import ContextDev from "context.dev";

const client = new ContextDev({
  apiKey: process.env.CONTEXT_DEV_API_KEY,
});

const site = await client.web.mapUrls({
  domain: "stripe.com",
  maxLinks: 50,
  urlRegex: "/customers/",
});

for (const entry of site.urls) {
  console.log(entry.url, entry.title);
}
```

```python Python theme={null}
import os
from context.dev import ContextDev

client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])

site = client.web.map_urls(
    domain="stripe.com",
    max_links=50,
    url_regex="/customers/",
)

for entry in site.urls:
    print(entry.url, entry.title)
```

```ruby Ruby theme={null}
require "cgi/core"
require "context_dev"

client = ContextDev::Client.new(api_key: ENV.fetch("CONTEXT_DEV_API_KEY"))

site = client.web.map_urls(
  domain: "stripe.com",
  max_links: 50,
  url_regex: "/customers/",
)

site.urls.each do |entry|
  puts "#{entry.url} #{entry.title}"
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
)

func main() {
    client := contextdev.NewClient(
        option.WithAPIKey(os.Getenv("CONTEXT_DEV_API_KEY")),
    )

    site, err := client.Web.MapURLs(context.Background(), contextdev.WebMapURLsParams{
        Domain:   "stripe.com",
        MaxLinks: contextdev.Int(50),
        URLRegex: contextdev.String("/customers/"),
    })
    if err != nil {
        panic(err)
    }

    for _, entry := range site.URLs {
        fmt.Println(entry.URL, entry.Title)
    }
}
```

```php PHP theme={null}
<?php

require __DIR__.'/vendor/autoload.php';

use ContextDev\Client;

$client = new Client(apiKey: getenv('CONTEXT_DEV_API_KEY'));

$site = $client->web->mapUrls(
    domain: 'stripe.com',
    maxLinks: 50,
    urlRegex: '/customers/',
);

foreach ($site->urls as $entry) {
    echo $entry->url, ' ', $entry->title ?? '', PHP_EOL;
}
```

```bash cURL theme={null}
curl --get https://api.context.dev/v1/web/urls \
  --header "Authorization: Bearer $CONTEXT_DEV_API_KEY" \
  --data-urlencode "domain=stripe.com" \
  --data-urlencode "maxLinks=50" \
  --data-urlencode "urlRegex=/customers/"
```

Abridged response:

```json theme={null}
{"success":true,"domain":"stripe.com","urls":[{"url":"https://stripe.com/pricing","title":"Pricing"}]}
```

## Request options

[Filters and search](https://docs.context.dev/map/filter-and-search.md) covers `maxLinks`, `urlRegex`, `excludeUrlRegex`, `includeSubdomains`, `sitemapUrl`, and `search`. These query parameters apply to any map request:

| Parameter | Values |
| - | - |
| `timeoutOpts` | `timeoutOpts[milliseconds]`, 1–300,000, and `timeoutOpts[behavior]`: `fail` returns 408 at the deadline; `return-partial` returns available results, so inspect `partial`. Without `timeoutOpts`, a map request stops at 45,000 ms and returns partial results. When you send `timeoutOpts` without a behavior, it defaults to `fail`. See [Timeouts](https://docs.context.dev/optimization/timeouts.md). |
| `zdr` | `enabled` turns on [zero data retention](https://docs.context.dev/optimization/zero-data-retention.md); defaults to `disabled`. Returns `403 ZDR_NOT_ENABLED` unless your organization has ZDR. |
| `policies` | Comma-separated [access policy](https://docs.context.dev/optimization/access-policies.md) IDs. A URL must pass every policy. |
| `tags` | Comma-separated [request tags](https://docs.context.dev/optimization/usage-and-logs.md), up to 20, each 1–50 characters. |

## Use the results

Choose relevant URLs and pass them to [Scrape](https://docs.context.dev/scrape/overview) or [Batches](https://docs.context.dev/batches/overview). [Filters and search](https://docs.context.dev/map/filter-and-search.md) narrow the returned inventory.

Newly discovered URLs can lack metadata while background enrichment runs. ZDR or custom headers return URLs without shared metadata enrichment. Responses are not cached as a complete inventory; inspect `partial` if a deadline stopped processing.

See the [Map reference](https://docs.context.dev/api-reference/web-scraping/map.md) for the complete query and response.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.